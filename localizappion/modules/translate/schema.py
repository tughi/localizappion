import graphene
from sqlalchemy.orm import contains_eager

from localizappion.models import String
from localizappion.models import Suggestion


class TranslationType(graphene.ObjectType):
    uuid = graphene.String()
    language = graphene.Field(lambda: LanguageType)
    strings = graphene.List(lambda: StringType)

    def resolve_strings(self, info):
        translation = info.context.translation
        return translation.project.strings_query \
            .outerjoin(Suggestion, (String.id == Suggestion.string_id) & (Suggestion.translation == translation) & (Suggestion.accepted.__eq__(True))) \
            .options(contains_eager(String.suggestions)) \
            .order_by(String.position) \
            .all()


class LanguageType(graphene.ObjectType):
    code = graphene.String()
    name = graphene.String()
    plurals_zero = graphene.String()
    plurals_one = graphene.String()
    plurals_two = graphene.String()
    plurals_few = graphene.String()
    plurals_many = graphene.String()
    plurals_other = graphene.String()


class StringType(graphene.ObjectType):
    name = graphene.String()
    position = graphene.Int()
    suggestions = graphene.List(lambda: PluralSuggestionsType)

    def resolve_suggestions(self, info):
        if self.value_one:
            return [dict(plural_form=plural_form, suggestions=self.suggestions) for plural_form in info.context.translation.language.plural_forms]
        return [dict(plural_form='other', suggestions=self.suggestions)]


class PluralSuggestionsType(graphene.ObjectType):
    plural_form = graphene.String()
    accepted = graphene.List(lambda: SuggestionType)

    def resolve_plural_form(self, info):
        return self['plural_form']

    def resolve_accepted(self, info):
        plural_form = self['plural_form']
        return [suggestion for suggestion in self['suggestions'] if suggestion.plural_form == plural_form]


class SuggestionType(graphene.ObjectType):
    value = graphene.String()
    votes_value = graphene.Int()


class Query(graphene.ObjectType):
    translation = graphene.Field(TranslationType)

    def resolve_translation(self, info):
        return info.context.translation


schema = graphene.Schema(query=Query)
