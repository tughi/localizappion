import graphene
import graphene_sqlalchemy

from models import Language
from models import Project
from models import String
from models import Suggestion
from models import Translation
from models import Translator
from models import Vote
from models import db_session


class LanguageType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Language


class ProjectType(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = Project


class StringType(graphene_sqlalchemy.SQLAlchemyObjectType):
    id = graphene.Int()
    suggestions = graphene.List(lambda: SuggestionType, accepted=graphene.Boolean(), language_code=graphene.String())

    def resolve_suggestions(self, info, accepted=None, language_code=None):
        suggestions = self.suggestions.join(Suggestion.translation, Translation.language)
        if accepted is not None:
            suggestions = suggestions.filter(Suggestion.accepted == accepted)
        if language_code is not None:
            suggestions = suggestions.filter(Language.code == language_code)
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
    languages = graphene.List(LanguageType)
    projects = graphene.List(ProjectType)
    strings = graphene.List(StringType, project_uuid=graphene.String())
    translators = graphene.List(TranslatorType)

    def resolve_languages(self, info):
        return db_session.query(Language).all()

    def resolve_projects(self, info):
        return db_session.query(Project)

    def resolve_strings(self, info, project_uuid=None):
        strings = db_session.query(String)
        if project_uuid is not None:
            strings = strings.join(Project).filter(Project.uuid == project_uuid)
        return strings

    def resolve_translators(self, info):
        return db_session.query(Translator).all()


schema = graphene.Schema(query=Query)
