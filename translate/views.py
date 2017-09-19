from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

from .models import Language
from .models import Project
from .models import String


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

    suggestions_required, suggestions_submitted, suggestions_voted = get_progress(project, language)

    return JsonResponse(dict(
        language_code=language.code,
        suggestions_required=suggestions_required,
        suggestions_submitted=suggestions_submitted,
    ))


def get_progress(project, language):
    required_suggestions = 0
    submitted_suggestions = 0
    voted_suggestions = 0

    strings = String.objects.filter(project=project)
    for string in strings:
        suggestions = {}
        for suggestion in string.suggestions.filter(language=language).annotate(votes_value=Sum('votes__value')):
            if suggestion.plural_form in suggestions:
                suggestions[suggestion.plural_form] = suggestion.votes_value > 1 or suggestions[suggestion.plural_form]
            else:
                suggestions[suggestion.plural_form] = suggestion.votes_value > 1

        required_suggestions += 1
        if 'other' in suggestions:
            submitted_suggestions += 1
            if suggestions['other']:
                voted_suggestions += 1

        if string.value_one:
            if language.plurals_zero:
                required_suggestions += 1
                if 'zero' in suggestions:
                    submitted_suggestions += 1
                    if suggestions['zero']:
                        voted_suggestions += 1

            if language.plurals_one:
                required_suggestions += 1
                if 'one' in suggestions:
                    submitted_suggestions += 1
                    if suggestions['one']:
                        voted_suggestions += 1

            if language.plurals_two:
                required_suggestions += 1
                if 'two' in suggestions:
                    submitted_suggestions += 1
                    if suggestions['two']:
                        voted_suggestions += 1

            if language.plurals_few:
                required_suggestions += 1
                if 'few' in suggestions:
                    submitted_suggestions += 1
                    if suggestions['few']:
                        voted_suggestions += 1

            if language.plurals_many:
                required_suggestions += 1
                if 'many' in suggestions:
                    submitted_suggestions += 1
                    if suggestions['many']:
                        voted_suggestions += 1

    return required_suggestions, submitted_suggestions, voted_suggestions


def translate(request, translator_uuid, project_uuid, language_code):
    try:
        project = Project.objects.get(uuid=project_uuid)
    except Project.DoesNotExist:
        return render(request, 'translate/project_not_found.html', status=404)

    try:
        language = project.languages.get(code=language_code)
    except Language.DoesNotExist:
        return render(request, 'translate/language_not_found.html', context=dict(project=project), status=404)

    suggestions_required, suggestions_submitted, suggestions_voted = get_progress(project, language)

    voted_suggestions = int(100. * suggestions_voted / suggestions_required)
    submitted_suggestions = int(100. * suggestions_submitted / suggestions_required) - voted_suggestions

    context = dict(
        project=project,
        language=language,
        voted_suggestions=voted_suggestions,
        submitted_suggestions=submitted_suggestions,
    )

    return render(request, 'translate/translate.html', context=context)
