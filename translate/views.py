from datetime import datetime

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

from .models import Language
from .models import Project
from .models import String
from .models import Suggestion


def status(request, translator_uuid, project_uuid, language_code):
    try:
        project = Project.objects.get(uuid=project_uuid)
    except Project.DoesNotExist:
        return JsonResponse(dict(message="Project does not exist"), status=404)

    try:
        language = project.languages.get(code=language_code)
    except Language.DoesNotExist:
        try:
            language = project.languages.get(code=language_code.split('_')[0])
        except Language.DoesNotExist:
            return JsonResponse(dict(message="Language does not exist"), status=404)

    progress = Progress(project, language)

    return JsonResponse(dict(
        language_code=language.code,
        suggestions_required=progress.required_suggestions,
        suggestions_submitted=progress.submitted_suggestions,
    ))


def translate(request, translator_uuid, project_uuid, language_code):
    try:
        project = Project.objects.get(uuid=project_uuid)
    except Project.DoesNotExist:
        return render(request, 'translate/project_not_found.html', status=404)

    try:
        language = project.languages.get(code=language_code)
    except Language.DoesNotExist:
        return render(request, 'translate/language_not_found.html', context=dict(project=project), status=404)

    # FIXME: this query ignores plural forms
    string = project.strings.difference(
        String.objects.filter(
            project=project,
            suggestions__language=language,
            suggestions__votes__translator__uuid=translator_uuid
        )
    ).order_by('last_access_time').first()

    string.last_access_time = datetime.now()
    string.save()

    suggestions = Suggestion.objects.filter(string=string, language=language, plural_form='other')

    context = dict(
        project=project,
        language=language,
        progress=Progress(project, language),
        string=string,
        suggestions=suggestions,
    )

    return render(request, 'translate/translate.html', context=context)


class Progress:
    def __init__(self, project, language):
        self.required_suggestions = 0
        self.submitted_suggestions = 0
        self.voted_suggestions = 0

        strings = String.objects.filter(project=project)
        for string in strings:
            suggestions = {}
            for suggestion in string.suggestions.filter(language=language).annotate(votes_value=Sum('votes__value')):
                if suggestion.plural_form in suggestions:
                    suggestions[suggestion.plural_form] = (suggestion.votes_value or 0) > 1 or suggestions[suggestion.plural_form]
                else:
                    suggestions[suggestion.plural_form] = (suggestion.votes_value or 0) > 1

            self.required_suggestions += 1
            if 'other' in suggestions:
                self.submitted_suggestions += 1
                if suggestions['other']:
                    self.voted_suggestions += 1

            if string.value_one:
                for plural_form in language.plural_forms:
                    if plural_form != 'other':
                        self.required_suggestions += 1
                        if plural_form in suggestions:
                            self.submitted_suggestions += 1
                            if suggestions[plural_form]:
                                self.voted_suggestions += 1

    @property
    def percentage_voted(self):
        return int(100. * self.voted_suggestions / self.required_suggestions)

    @property
    def percentage_submitted_only(self):
        return int(100. * (self.submitted_suggestions - self.voted_suggestions) / self.required_suggestions)
