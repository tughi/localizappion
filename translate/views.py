from django.http import JsonResponse

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

    suggestions_required = 0
    suggestions_submitted = 0

    strings = String.objects.filter(project=project)
    for string in strings:
        suggestions = {}
        for suggestion in string.suggestions.filter(language=language):
            if suggestion.plural_form in suggestions:
                suggestions[suggestion.plural_form] += 1
            else:
                suggestions[suggestion.plural_form] = 1

        suggestions_required += 1
        if 'other' in suggestions:
            suggestions_submitted += 1

        if string.value_one:
            if language.plurals_zero:
                suggestions_required += 1
                if 'zero' in suggestions:
                    suggestions_submitted += 1

            if language.plurals_one:
                suggestions_required += 1
                if 'one' in suggestions:
                    suggestions_submitted += 1

            if language.plurals_two:
                suggestions_required += 1
                if 'two' in suggestions:
                    suggestions_submitted += 1

            if language.plurals_few:
                suggestions_required += 1
                if 'few' in suggestions:
                    suggestions_submitted += 1

            if language.plurals_many:
                suggestions_required += 1
                if 'many' in suggestions:
                    suggestions_submitted += 1

    return JsonResponse(dict(
        language_code=language.code,
        suggestions_required=suggestions_required,
        suggestions_submitted=suggestions_submitted,
    ))
