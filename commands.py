import os

from models import Base
from models import Language
from models import Project
from models import String
from models import Suggestion
from models import Translation
from models import Translator
from models import Vote
from models import db_session


def init_db():
    Base.metadata.create_all(db_session.bind)

    # import data

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
            db_session.add(language)
            db_session.flush()
            languages[language.code] = language.id

    projects = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'projects.txt')) as data_file:
        for line in data_file:
            project_uuid, project_name = map(str.strip, line.split('|', 1))
            project = Project(
                uuid=project_uuid,
                name=project_name,
            )
            db_session.add(project)
            db_session.flush()
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
            db_session.add(string)
            db_session.flush()
            strings[(project_id, string_name)] = string.id

    translators = {}
    with open(os.path.join(os.path.dirname(__file__), 'db_data', 'translators.txt')) as data_file:
        for line in data_file:
            alias, email_hash = map(str.strip, line.split('|')[0:2])
            translator = Translator(
                email_hash=email_hash,
                alias=alias,
            )
            db_session.add(translator)
            db_session.flush()
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
                db_session.add(translation)
                db_session.flush()
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
                db_session.add(suggestion)
                db_session.flush()
                suggestions[(translation_id, string_id, value, plural_form)] = suggestion_id = suggestion.id
            db_session.add(Vote(
                suggestion_id=suggestion_id,
                translator_id=translator_id,
                value=1,
            ))

    db_session.commit()
