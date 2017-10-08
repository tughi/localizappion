from xml.etree import ElementTree

from django import views
from django.shortcuts import render

from .models import Project


class ProjectStringsView(views.View):
    @staticmethod
    def get(request, project_uuid=None):
        return render(request, 'core/project_strings.html', dict(
            project=Project.objects.get(uuid=project_uuid)
        ))


class UploadStringsXmlView(views.View):
    class UploadError(Exception):
        def __init__(self, message):
            self.message = message

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
                raise UploadStringsXmlView.UploadError("Not a valid strings.xml file")

            if resources.tag != 'resources':
                raise UploadStringsXmlView.UploadError("Not a valid strings.xml file")

            new_strings = {}

            def load_new_string(element, plural='other'):
                string_value = element.text or ''
                for element_child in element:
                    if element_child.tag == '{urn:oasis:names:tc:xliff:document:1.2}g':
                        # TODO: use element_child.text as marker
                        string_value += element_child.text
                        if element_child.tail:
                            string_value += element_child.tail
                    else:
                        raise UploadStringsXmlView.UploadError("Unsupported string tag: {0}".format(element_child.tag))
                return {
                    'value_' + plural: string_value.strip(),
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
                            position=new_string['position'],
                        ))
                    else:
                        changes.append(dict(
                            action='update',
                            name=old_string.name,
                            value_one=old_string.value_one,
                            value_other=old_string.value_other,
                            position=new_string['position'],
                        ))
                    del new_strings[old_string.name]
            changes.extend(new_strings.values())

            changes.sort(key=lambda item: (item['position'], item['action']))

            return render(request, 'core/project_strings_upload.html', dict(
                project=project,
                changes=changes,
            ))
        except UploadStringsXmlView.UploadError as upload_error:
            return render(request, 'core/project_strings_upload_error.html', dict(project=project, message=upload_error.message))
