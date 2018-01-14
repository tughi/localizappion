import base64
import os

import graphene
import graphene_sqlalchemy
from flask import url_for

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
    screenshot = graphene.Field(lambda: ScreenshotType, id=graphene.ID(required=True))
    screenshots_count = graphene.Field(graphene.Int)
    strings_count = graphene.Field(graphene.Int)

    def resolve_screenshot(self: Project, info, id):
        return Screenshot.query.filter(Screenshot.id == id, Screenshot.project_id == self.id).one()

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
        return url_for('static', filename='screenshots/{uuid}/{name}'.format(uuid=self.project.uuid, name=self.name))

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


class CreateScreenshot(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        content = graphene.String(required=True)

    project = graphene.Field(ProjectType)

    def mutate(self, info, project_id, name, content: str):
        project = Project.query.get(project_id)

        data, content = content.split(':', 1)
        assert data == 'data'

        content_type, content = content.split(';', 1)

        encoding, content = content.split(',', 1)
        assert encoding == 'base64'

        content = base64.b64decode(content)

        screenshots_dir = os.path.join(os.path.dirname(__file__), 'static', 'screenshots', project.uuid)
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_file = os.path.join(screenshots_dir, name)
        if os.path.exists(screenshot_file):
            raise FileExistsError('Screenshot file already exists')
        with open(screenshot_file, mode='wb') as file:
            file.write(content)

        db.session.add(Screenshot(
            project_id=project_id,
            name=name,
            content_length=len(content),
            content_type=content_type,
        ))
        db.session.commit()

        return CreateScreenshot(project=project)


class AddProjectScreenshotString(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        screenshot_id = graphene.ID(required=True)
        string_id = graphene.ID(required=True)

    project = graphene.Field(ProjectType)

    def mutate(self, info, project_id, screenshot_id, string_id):
        screenshot = Screenshot.query.filter(Screenshot.id == screenshot_id, Screenshot.project_id == project_id).first()
        string = String.query.filter(String.id == string_id, String.project_id == project_id).first()

        if screenshot and string:
            db.session.add(ScreenshotString(screenshot=screenshot, string=string))
            db.session.commit()

            return AddProjectScreenshotString(project=screenshot.project)

        return AddProjectScreenshotString(project=None)


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


class Mutation(graphene.ObjectType):
    create_screenshot = CreateScreenshot.Field()
    add_project_screenshot_string = AddProjectScreenshotString.Field()
    delete_project_screenshot = DeleteProjectScreenshot.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
