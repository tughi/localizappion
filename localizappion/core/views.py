import json
from datetime import datetime
from xml.etree import ElementTree

from django import views
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required
from django.db import models
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from google.cloud import translate as google_translate

from .models import Project
from .models import String
from .models import Suggestion
from .models import Translation
from .models import Vote


class LoginView(views.View):
    @staticmethod
    def get(request):
        return render(request, 'core/login.html', dict(next=request.META['HTTP_REFERER']))

    @staticmethod
    def post(request):
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect(request.POST['next'] or 'project_list')
        return render(request, 'core/login.html', dict(next=request.POST['next']))


class LogoutView(views.View):
    @staticmethod
    def get(request):
        logout(request)
        referrer = request.META['HTTP_REFERER']
        return redirect(referrer)


class ProjectListView(views.View):
    @staticmethod
    def get(request):
        return render(request, 'core/project_list.html', dict(
            projects=Project.objects.all(),
        ))


class ProjectStatusView(views.View):
    @staticmethod
    def get(request, project_uuid=None):
        project = Project.objects.get(uuid=project_uuid)
        return render(request, 'core/project_status.html', dict(
            project=project,
        ))


class ProjectStringsView(views.View):
    @staticmethod
    def get(request, project_uuid=None):
        return render(request, 'core/project_strings.html', dict(
            project=Project.objects.get(uuid=project_uuid)
        ))

    @staticmethod
    @permission_required('core.can_add_string')
    def post(request, project_uuid=None):
        project = Project.objects.get(uuid=project_uuid)

        strings_xml = request.FILES['strings_xml']
        strings_xml_content = bytes.decode(strings_xml.read(), 'utf-8')

        try:
            try:
                resources = ElementTree.fromstring(strings_xml_content)
            except ElementTree.ParseError:
                # TODO: log the parse error
                raise UploadError("Not a valid XML file")

            if resources.tag != 'resources':
                raise UploadError("Unexpected root tag: {0}".format(resources.tag))

            new_strings = {}

            def load_new_string(element, plural='other'):
                markers = {}
                string_value = element.text or ''
                for element_child in element:
                    if element_child.tag == '{urn:oasis:names:tc:xliff:document:1.2}g':
                        markers[element_child.text] = dict(name=element_child.get('id'))
                        string_value += element_child.text
                        if element_child.tail:
                            string_value += element_child.tail
                    else:
                        raise UploadError("Unsupported string tag: {0}".format(element_child.tag))
                return {
                    'value_' + plural: string_value.strip().replace('\\\'', '\'').replace('\\"', '"').replace('\\n', '\n'),
                    'markers': json.dumps(markers) if markers else '',
                }

            for resource in resources:
                if resource.get('translatable') == 'false':
                    continue

                string_name = resource.get('name')
                if resource.tag == 'string':
                    new_string = load_new_string(resource)
                    new_string['value_one'] = ''
                elif resource.tag == 'plurals':
                    new_string = {}
                    for resource_item in resource:
                        new_string.update(load_new_string(resource_item, plural=resource_item.get('quantity')))
                else:
                    continue
                new_string['action'] = 'add'
                new_string['name'] = string_name
                new_string['position'] = len(new_strings) + 1
                new_strings[string_name] = new_string

            changes = []
            for old_string in project.strings.all():
                if old_string.name not in new_strings:
                    changes.append(dict(
                        action='remove',
                        name=old_string.name,
                        value_one=old_string.value_one,
                        value_other=old_string.value_other,
                        markers=old_string.markers,
                        position=old_string.position,
                    ))
                else:
                    new_string = new_strings[old_string.name]
                    if new_string['value_one'] != old_string.value_one or new_string['value_other'] != old_string.value_other:
                        changes.append(dict(
                            action='merge',
                            name=old_string.name,
                            value_one=new_string['value_one'],
                            value_other=new_string['value_other'],
                            markers=new_string['markers'],
                            old_value_one=old_string.value_one,
                            old_value_other=old_string.value_other,
                            old_markers=old_string.markers,
                            position=new_string['position'],
                        ))
                    else:
                        changes.append(dict(
                            action='update',
                            name=old_string.name,
                            value_one=new_string['value_one'],
                            value_other=new_string['value_other'],
                            markers=new_string['markers'],
                            position=new_string['position'],
                        ))
                    del new_strings[old_string.name]
            changes.extend(new_strings.values())

            changes.sort(key=lambda item: (item['position'], item['action']))

            request.session['PROJECT_STRINGS_CHANGES'] = changes

            return render(request, 'core/project_strings_upload.html', dict(
                project=project,
                changes=changes,
            ))
        except UploadError as upload_error:
            return render(request, 'core/project_strings_upload_error.html', dict(project=project, message=upload_error.message))


class ProjectStringsCommitView(views.View):
    @staticmethod
    @permission_required('core.can_add_string')
    def post(request, project_uuid):
        project = Project.objects.get(uuid=project_uuid)

        changes = request.session['PROJECT_STRINGS_CHANGES']

        try:
            with transaction.atomic():
                for change in changes:
                    action = change['action']
                    if action == 'add':
                        String.objects.create(
                            project=project,
                            name=change['name'],
                            value_one=change['value_one'],
                            value_other=change['value_other'],
                            markers=change['markers'],
                            position=change['position'],
                        )
                    elif action == 'merge':
                        merge_action = request.POST[change['name']]
                        if merge_action == 'keep_suggestions':
                            Vote.objects.filter(
                                suggestion__string__project=project,
                                suggestion__string__name=change['name'],
                            ).delete()
                        elif merge_action == 'remove_suggestions':
                            Suggestion.objects.filter(
                                string__project=project,
                                string__name=change['name'],
                            ).delete()
                        else:
                            raise UploadError("Unsupported merge action: {0}".format(merge_action))
                        String.objects.filter(project=project, name=change['name']).update(
                            value_one=change['value_one'],
                            value_other=change['value_other'],
                            markers=change['markers'],
                            position=change['position'],
                        )
                    elif action == 'remove':
                        String.objects.filter(project=project, name=change['name']).delete()
                    elif action == 'update':
                        String.objects.filter(project=project, name=change['name']).update(
                            value_one=change['value_one'],
                            value_other=change['value_other'],
                            markers=change['markers'],
                            position=change['position'],
                        )
                    else:
                        raise UploadError("Unsupported action: {0}".format(action))
            project.strings_upload_time = datetime.now()
            project.save()
        except UploadError as upload_error:
            return render(request, 'core/project_strings_upload_error.html', dict(project=project, message=upload_error.message))

        del request.session['PROJECT_STRINGS_CHANGES']

        return redirect('project_strings', project_uuid=project.uuid)


class UploadError(Exception):
    def __init__(self, message):
        self.message = message


class ProjectNewSuggestions(views.View):
    @staticmethod
    def get(request, project_uuid):
        project = Project.objects.get(uuid=project_uuid)
        suggestion = project.first_new_suggestion()
        if suggestion:
            return redirect('project_new_suggestion', project_uuid, suggestion.uuid)
        return redirect('project', project_uuid)


class ProjectNewSuggestion(views.View):
    @staticmethod
    def get(request, project_uuid, suggestion_uuid):
        project = Project.objects.get(uuid=project_uuid)
        suggestion = Suggestion.objects.get(uuid=suggestion_uuid, translation__project=project)

        other_suggestions = suggestion.string.suggestions.exclude(id=suggestion.id).filter(
            translation=suggestion.translation,
            plural_form=suggestion.plural_form
        )

        return render(request, 'core/project_new_suggestion.html', dict(
            project=project,
            suggestion=suggestion,
            suggestion_votes=suggestion.votes.count(),
            other_suggestions=other_suggestions,
        ))


class ProjectNewSuggestionAccept(views.View):
    @staticmethod
    def get(request, project_uuid, suggestion_uuid):
        project = Project.objects.get(uuid=project_uuid)
        suggestion = Suggestion.objects.get(uuid=suggestion_uuid, translation__project=project)
        suggestion.accepted = True
        suggestion.save()
        return redirect('project_new_suggestions', project_uuid)


class ProjectNewSuggestionReject(views.View):
    @staticmethod
    def get(request, project_uuid, suggestion_uuid):
        project = Project.objects.get(uuid=project_uuid)
        suggestion = Suggestion.objects.get(uuid=suggestion_uuid, translation__project=project)
        suggestion.accepted = False
        suggestion.save()
        return redirect('project_new_suggestions', project_uuid)


class ProjectTranslation(views.View):
    @staticmethod
    def get(request, project_uuid, language_code):
        translation = Translation.objects.filter(language__code=language_code, project__uuid=project_uuid).select_related('project').get()
        project = translation.project

        suggestions = Suggestion.objects.filter(translation=translation, accepted=True)
        suggestions = suggestions.values('string_id', 'value', 'plural_form', 'added_time', 'google_translation')
        suggestions = suggestions.annotate(votes_value=models.Sum('votes__value'))
        suggestions = list(suggestions)

        strings = []
        for string in String.objects.filter(project=project):
            string_values = dict(
                name=string.name,
                value_one=string.value_one,
                value_other=string.value_other,
                suggestions=[],
            )
            for plural_form in translation.language.plural_forms if string.value_one else ('other',):
                string_values['suggestions'].append((
                    plural_form,
                    sorted(
                        filter(lambda suggestion: suggestion['string_id'] == string.id and suggestion['plural_form'] == plural_form, suggestions),
                        key=lambda suggestion: (suggestion['votes_value'], -suggestion['added_time'].timestamp()),
                        reverse=True,
                    )
                ))

            strings.append(string_values)

        return render(request, 'core/project_translation.html', dict(
            project=project,
            translation=translation,
            strings=strings,
        ))


class TranslateSuggestions(views.View):
    @staticmethod
    def get(request):
        suggestion = Suggestion.objects.filter(accepted=None, google_translation=None).select_related('translation__language').first()

        if suggestion:
            google_translate_client = google_translate.Client()
            suggestion_translation = google_translate_client.translate(
                values=suggestion.value,
                source_language=suggestion.translation.language.code,
                target_language='en',
            )

            suggestion.google_translation = suggestion_translation.get('translatedText')
            suggestion.save()

            return JsonResponse(dict(success=True))

        return JsonResponse(dict(success=False))
