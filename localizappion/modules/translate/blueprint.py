import json

import flask
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from localizappion.models import PLURAL_FORMS
from localizappion.models import String
from localizappion.models import Suggestion
from localizappion.models import SuggestionVote
from localizappion.models import Translation
from localizappion.models import TranslatorSession

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


class Void:
    def __init__(self, prefix=None):
        self.prefix = prefix

    def append(self, item):
        flask.current_app.logger.warning('{prefix}{item}'.format(prefix=self.prefix, item=item))


@blueprint.route('/api/v1/translations/<uuid:translation_uuid>:<uuid:translator_uuid>')
def get_translation(translation_uuid, translator_uuid):
    translator_session = TranslatorSession.query \
        .join(TranslatorSession.translator) \
        .options(contains_eager(TranslatorSession.translator)) \
        .filter(TranslatorSession.activated_time.isnot(None)) \
        .filter(TranslatorSession.uuid == str(translator_uuid)) \
        .first()
    if not translator_session:
        return flask.abort(404)

    translator = translator_session.translator

    translation = Translation.query \
        .options(joinedload(Translation.project), joinedload(Translation.language)) \
        .filter(Translation.uuid == str(translation_uuid)) \
        .first()
    if not translation:
        return flask.abort(404)

    project = translation.project

    language = translation.language
    language_plural_forms = language.plural_forms

    strings = project.strings_query \
        .outerjoin(Suggestion, (String.id == Suggestion.string_id) & (Suggestion.translation == translation) & (Suggestion.accepted.__eq__(True))) \
        .options(contains_eager(String.suggestions)) \
        .order_by(String.position, Suggestion.votes_value.desc(), Suggestion.added_time)

    # TODO: select only the suggestions made in this translation
    voted_suggestions = set(result[0] for result in SuggestionVote.query.filter(SuggestionVote.translator == translator).values(SuggestionVote.suggestion_id))

    def _as_suggestion_data(suggestion):
        suggestion_data = dict(
            value=suggestion.value,
            votes=suggestion.votes_value,
        )
        if suggestion.id in voted_suggestions:
            suggestion_data['voted'] = True
        return suggestion_data

    ignored_suggestions = {plural_form: Void('Discarded "{}" suggestion: '.format(plural_form)) for plural_form, plural_form_name in PLURAL_FORMS}

    strings_data = []
    for string in strings:
        string_data = dict(
            name=string.name,
        )
        if string.markers:
            string_data['markers'] = json.loads(string.markers)
        if string.value_one:
            string_data.update(dict(
                value=dict(
                    one=string.value_one,
                    other=string.value_other,
                )
            ))
            suggestions_data = string_data['suggestions'] = {plural_form: [] for plural_form in language_plural_forms}
            for suggestion in string.suggestions:
                suggestions_data.get(suggestion.plural_form, ignored_suggestions[suggestion.plural_form]).append(_as_suggestion_data(suggestion))
        else:
            string_data.update(dict(
                value=string.value_other,
            ))
            suggestions_data = string_data['suggestions'] = []
            for suggestion in string.suggestions:
                if suggestion.plural_form == 'other':
                    suggestions_data.append(_as_suggestion_data(suggestion))

        strings_data.append(string_data)

    return flask.jsonify(
        project=dict(
            name=project.name,
        ),
        language=dict(
            code=language.code,
            name=language.name,
            plurals={
                plural_form: language.get_examples(plural_form) for plural_form in language_plural_forms
            },
        ),
        strings=strings_data,
    )
