from xml.etree import ElementTree

from django import views
from django.shortcuts import render, redirect

from .models import Project


class ProjectStringsView(views.View):
    @staticmethod
    def get(request, project_uuid=None):
        return render(request, 'core/project_strings.html', dict(
            project=Project.objects.get(uuid=project_uuid)
        ))


class ImportStringsXmlView(views.View):
    @staticmethod
    def post(request, project_uuid=None):
        project = Project.objects.get(uuid=project_uuid)
        project_strings = set(project.strings.values_list('name', flat=True))

        strings_xml = request.FILES['strings_xml']
        strings_xml_content = bytes.decode(strings_xml.read(), 'utf-8')

        resources = ElementTree.fromstring(strings_xml_content)
        if resources.tag != 'resources':
            # TODO: fail with error: not a valid strings.xml file
            pass
        else:
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
                        # TODO: fail with error: unsupported tag
                        pass
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
                        position=old_string.position
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
                            position=new_string['position']
                        ))
                    else:
                        changes.append(dict(
                            action='update',
                            name=old_string.name,
                            value_one=old_string.value_one,
                            value_other=old_string.value_other,
                            position=new_string['position']
                        ))
                    del new_strings[old_string.name]
            changes.extend(new_strings.values())

            changes.sort(key=lambda item: (item['position'], item['action']))

            context = {
                'project': project,
                'changes': changes,
            }
            return render(request, 'core/project_strings_upload.html', context)

        return redirect(url_for('project_strings', project_uuid=project_uuid))
