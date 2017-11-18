import graphene
import graphene_sqlalchemy

from .models import Language
from .models import Project
from .models import String
from .models import Suggestion
from .models import Translation
from .models import Translator
from .models import Vote
from .models import db


class LanguageType(graphene_sqlalchemy.SQLAlchemyObjectType):
    plural_forms = graphene.List(graphene.String)

    class Meta:
        model = Language


class ProjectType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Project


class StringType(graphene_sqlalchemy.SQLAlchemyObjectType):
    suggestions = graphene.List(lambda: SuggestionType, accepted=graphene.Boolean(), language_code=graphene.String(), plural_form=graphene.String())

    def resolve_suggestions(self, info, accepted=None, language_code=None, plural_form=None):
        suggestions = self.suggestions.join(Suggestion.translation, Translation.language).order_by(Suggestion.votes_value.desc(), Suggestion.added_time)
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


class VoteType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    languages = graphene.List(LanguageType, language_code=graphene.String())
    projects = graphene.List(ProjectType)
    strings = graphene.List(StringType, project_uuid=graphene.String())
    translations = graphene.List(TranslationType, language_code=graphene.String())

    def resolve_languages(self, info, language_code=None):
        languages = db.session.query(Language)
        if language_code is not None:
            languages = languages.filter(Language.code == language_code)
        return languages

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


schema = graphene.Schema(query=Query)
