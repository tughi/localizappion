import json
from datetime import datetime
from xml.etree import ElementTree

from django import views
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render

from .models import Project
from .models import String
from .models import Suggestion
from .models import Vote


class ProjectStringsView(views.View):
    @staticmethod
    def get(request, project_uuid=None):
        return render(request, 'core/project_strings.html', dict(
            project=Project.objects.get(uuid=project_uuid)
        ))

    @staticmethod
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
                            old_value_one=old_string.value_one,
                            old_value_other=old_string.value_other,
                            markers=new_string['markers'],
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
