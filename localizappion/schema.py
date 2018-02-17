import base64
import hashlib
import os

import graphene
import graphene_sqlalchemy
from flask import url_for
from sqlalchemy.exc import DatabaseError

from .models import Language
from .models import Project
from .models import Screenshot
from .models import ScreenshotString
from .models import String
from .models import Suggestion
from .models import SuggestionVote
from .models import Translation
from .models import Translator
from .models import db


class LanguageType(graphene_sqlalchemy.SQLAlchemyObjectType):
    plural_forms = graphene.List(graphene.String)

    class Meta:
        model = Language


class ProjectType(graphene_sqlalchemy.SQLAlchemyObjectType):
    new_suggestion = graphene.Field(lambda: SuggestionType)
    new_suggestions_count = graphene.Field(graphene.Int)
    screenshot = graphene.Field(lambda: ScreenshotType, id=graphene.ID(required=False))
    screenshots_count = graphene.Field(graphene.Int)
    strings_count = graphene.Field(graphene.Int)

    def resolve_new_suggestion(self: Project, info):
        return Suggestion.query.join(Suggestion.translation) \
            .filter(Translation.project_id == self.id, Suggestion.accepted.__eq__(None)) \
            .first()

    def resolve_new_suggestions_count(self: Project, info):
        return db.session.query(Suggestion.id) \
            .join(Suggestion.translation) \
            .filter(Translation.project_id == self.id, Suggestion.accepted.__eq__(None)) \
            .count()

    def resolve_screenshot(self: Project, info, id=None):
        if id:
            return Screenshot.query.filter(Screenshot.id == id, Screenshot.project_id == self.id).one()
        return None

    def resolve_screenshots_count(self: Project, info):
        return Screenshot.query.filter(Screenshot.project_id == self.id).count()

    def resolve_strings_count(self: Project, info):
        return String.query.filter(String.project_id == self.id).count()

    def resolve_translations(self: Project, info):
        return self.translations_query.join(Translation.language).order_by(Language.name)

    class Meta:
        model = Project


class ScreenshotType(graphene_sqlalchemy.SQLAlchemyObjectType):
    url = graphene.Field(graphene.String)

    def resolve_url(self: Screenshot, info):
        return url_for('static', filename='screenshots/{uuid}/{file_name}'.format(uuid=self.project.uuid, file_name=self.file_name))

    class Meta:
        model = Screenshot


class ScreenshotStringType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = ScreenshotString


class StringType(graphene_sqlalchemy.SQLAlchemyObjectType):
    suggestions = graphene.List(lambda: SuggestionType, accepted=graphene.Boolean(), language_code=graphene.String(), plural_form=graphene.String())

    def resolve_suggestions(self: String, info, accepted=None, language_code=None, plural_form=None):
        suggestions = self.suggestions_query.join(Suggestion.translation, Translation.language).order_by(Suggestion.votes_value.desc(), Suggestion.added_time)
        if accepted is not None:
            suggestions = suggestions.filter(Suggestion.accepted == accepted)
        if language_code is not None:
            suggestions = suggestions.filter(Language.code == language_code)
        if plural_form is not None:
            suggestions = suggestions.filter(Suggestion.plural_form == plural_form)
        return suggestions

    class Meta:
        model = String


class TranslatorType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Translator


class TranslationType(graphene_sqlalchemy.SQLAlchemyObjectType):
    translated_strings_count = graphene.Field(graphene.Int)

    def resolve_translated_strings_count(self: Translation, info):
        return db.session.query(Suggestion.string_id) \
            .filter(Suggestion.translation_id == self.id, Suggestion.accepted.__eq__(True)) \
            .distinct() \
            .count()

    class Meta:
        model = Translation


class SuggestionType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Suggestion


class SuggestionVoteType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = SuggestionVote


class Query(graphene.ObjectType):
    languages = graphene.List(LanguageType, language_code=graphene.String())
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))
    projects = graphene.List(ProjectType)
    strings = graphene.List(StringType, project_uuid=graphene.String())
    translations = graphene.List(TranslationType, language_code=graphene.String())

    def resolve_languages(self, info, language_code=None):
        languages = db.session.query(Language)
        if language_code is not None:
            languages = languages.filter(Language.code == language_code)
        return languages

    def resolve_project(self, info, id):
        return db.session.query(Project).get(id)

    def resolve_projects(self, info):
        return db.session.query(Project)

    def resolve_strings(self, info, project_uuid=None):
        strings = db.session.query(String)
        if project_uuid is not None:
            strings = strings.join(Project).filter(Project.uuid == project_uuid)
        return strings

    def resolve_translations(self, info, language_code=None):
        translations = db.session.query(Translation)
        if language_code is not None:
            translations = translations.join(Language).filter(Language.code == language_code)
        return translations


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    project = graphene.Field(ProjectType)

    def mutate(self, info, name):
        project = Project(name=name)

        db.session.add(project)
        db.session.commit()

        return CreateProject(project=project)


class ScreenshotStringInputType(graphene.InputObjectType):
    id = graphene.ID(required=False)
    area = graphene.String(required=True)
    string_id = graphene.ID(required=True)


class SaveProjectScreenshot(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        screenshot_id = graphene.ID(required=False)
        screenshot_name = graphene.String(required=True)
        screenshot_data = graphene.String(required=False)
        screenshot_strings = graphene.List(ScreenshotStringInputType, required=True)

    screenshot = graphene.Field(ScreenshotType)

    def mutate(self, info, project_id, screenshot_id=None, screenshot_name=None, screenshot_data=None, screenshot_strings=None):
        project = Project.query.get(project_id)
        if screenshot_id:
            screenshot = Screenshot.query.filter(Screenshot.id == screenshot_id, Screenshot.project == project).one()
        else:
            screenshot = Screenshot(project=project)

        screenshot.name = screenshot_name

        screenshot_file = None
        if screenshot_data:
            data, screenshot_data = screenshot_data.split(':', 1)
            assert data == 'data'

            screenshot.file_type, screenshot_data = screenshot_data.split(';', 1)
            assert screenshot.file_type.startswith('image/')

            encoding, screenshot_data = screenshot_data.split(',', 1)
            assert encoding == 'base64'

            screenshot_data = base64.b64decode(screenshot_data)

            screenshot.file_name = hashlib.md5(screenshot_data).hexdigest() + '.' + screenshot.file_type.split('/', 1)[1]
            screenshot.file_size = len(screenshot_data)

            screenshots_dir = os.path.join(os.path.dirname(__file__), 'static', 'screenshots', project.uuid)
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_file = os.path.join(screenshots_dir, screenshot.file_name)
            if os.path.exists(screenshot_file):
                raise FileExistsError('Screenshot file already exists')
            with open(screenshot_file, mode='wb') as file:
                file.write(screenshot_data)

        try:
            db.session.add(screenshot)
            db.session.flush()

            for screenshot_string_data in screenshot_strings:
                screenshot_string_id = screenshot_string_data.id
                screenshot_string = ScreenshotString.query.get(screenshot_string_id) if screenshot_string_id else ScreenshotString(id=screenshot_string_id)
                screenshot_string.screenshot = screenshot
                screenshot_string.string = String.query.filter(String.id == screenshot_string_data.string_id, String.project == project).one()
                screenshot_string.area = screenshot_string_data.area
                db.session.add(screenshot_string)

            db.session.commit()
        except DatabaseError as error:
            if screenshot_file:
                os.remove(screenshot_file)
                raise error

        return SaveProjectScreenshot(screenshot=screenshot)


class DeleteProjectScreenshot(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        screenshot_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, project_id, screenshot_id):
        screenshot = Screenshot.query.filter(Screenshot.id == screenshot_id, Screenshot.project_id == project_id).first()

        if screenshot:
            screenshot_file = os.path.join(os.path.dirname(__file__), 'static', 'screenshots', screenshot.project.uuid, screenshot.name)

            db.session.delete(screenshot)
            db.session.commit()

            os.remove(screenshot_file)

            return DeleteProjectScreenshot(ok=True)

        return DeleteProjectScreenshot(ok=False)


class UpdateSuggestion(graphene.Mutation):
    class Arguments:
        suggestion_id = graphene.ID(required=True)
        accepted = graphene.Boolean(required=True)

    project = graphene.Field(ProjectType)

    def mutate(self, info, suggestion_id, accepted):
        suggestion = Suggestion.query.get(suggestion_id)

        suggestion.accepted = accepted

        db.session.add(suggestion)
        db.session.commit()

        return UpdateSuggestion(project=suggestion.translation.project)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    save_project_screenshot = SaveProjectScreenshot.Field()
    delete_project_screenshot = DeleteProjectScreenshot.Field()
    update_suggestion = UpdateSuggestion.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
