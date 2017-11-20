#!/usr/bin/env python
from flask_script import Manager
from flask_script import Server
from flask_script import Shell

from localizappion import app

manager = Manager(app)

manager.add_command("runserver", Server())
manager.add_command("shell", Shell())


@manager.command
def createdb():
    from localizappion.models import db

    db.drop_all()
    db.create_all()

    import os
    from localizappion.models import db
    from localizappion.models import Language
    from localizappion.models import Project
    from localizappion.models import String
    from localizappion.models import Translator
    from localizappion.models import Translation
    from localizappion.models import Suggestion
    from localizappion.models import Vote
    from localizappion.modules.registration import create_email_hash

    languages = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'languages.txt')) as data_file:
        for line in data_file:
            code, name, plurals_zero, plurals_one, plurals_two, plurals_few, plurals_many, plurals_other = map(str.strip, line.split('|'))
            language = Language(
                code=code,
                name=name,
                plurals_zero=plurals_zero or None,
                plurals_one=plurals_one or None,
                plurals_two=plurals_two or None,
                plurals_few=plurals_few or None,
                plurals_many=plurals_many or None,
                plurals_other=plurals_other or None,
            )
            db.session.add(language)
            db.session.flush()
            languages[language.code] = language.id

    projects = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'projects.txt')) as data_file:
        for line in data_file:
            project_uuid, project_name = map(str.strip, line.split('|', 1))
            project = Project(
                uuid=project_uuid,
                name=project_name,
            )
            db.session.add(project)
            db.session.flush()
            projects[project.uuid] = project.id

    strings = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'strings.txt')) as data_file:
        for line in data_file:
            project_uuid, string_name, string_value_other = map(str.strip, line.split('|', 2))
            project_id = projects[project_uuid]
            string = String(
                project_id=project_id,
                name=string_name,
                value_other=string_value_other,
            )
            db.session.add(string)
            db.session.flush()
            strings[(project_id, string_name)] = string.id

    translators = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'translators.txt')) as data_file:
        for line in data_file:
            alias, email = map(str.strip, line.split('|'))
            translator = Translator(
                email_hash=create_email_hash(email),
                alias=alias,
            )
            db.session.add(translator)
            db.session.flush()
            translators[translator.alias] = translator.id

    translations = {}
    suggestions = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'suggestions.txt')) as data_file:
        for line in data_file:
            project_uuid, string_name, language_code, translator_alias, plural_form, value = map(str.strip, line.split('|', 5))
            project_id = projects[project_uuid]
            language_id = languages[language_code]
            translation_id = translations.get((project_id, language_id))
            if not translation_id:
                translation = Translation(
                    project_id=project_id,
                    language_id=language_id,
                )
                db.session.add(translation)
                db.session.flush()
                translations[(project_id, language_id)] = translation_id = translation.id
            translator_id = translators[translator_alias]
            string_id = strings[(project_id, string_name)]
            suggestion_id = suggestions.get((translation_id, string_id, value, plural_form))
            if not suggestion_id:
                suggestion = Suggestion(
                    translation_id=translation_id,
                    translator_id=translator_id,
                    string_id=string_id,
                    value=value,
                    plural_form='other',
                )
                db.session.add(suggestion)
                db.session.flush()
                suggestions[(translation_id, string_id, value, plural_form)] = suggestion_id = suggestion.id
            db.session.add(Vote(
                suggestion_id=suggestion_id,
                translator_id=translator_id,
                value=1,
            ))

    db.session.commit()


manager.run()
