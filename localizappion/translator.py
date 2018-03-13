import json
from functools import wraps

import flask
from flask import render_template
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from localizappion.models import String
from localizappion.models import Suggestion
from localizappion.models import SuggestionVote
from localizappion.models import Translation
from localizappion.models import TranslatorSession
from localizappion.models import db

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


@blueprint.route('/translator/')
def index():
    return render_template(
        'translators/index.html',
    )


@blueprint.route('/translator/start-translating/<uuid:translator_session_uuid>-<uuid:translation_uuid>')
def translating_start(translator_session_uuid, translation_uuid):
    response = flask.make_response(flask.redirect('/translator/'))
    response.set_cookie('translator_session', str(translator_session_uuid))
    response.set_cookie('translation', str(translation_uuid))
    return response


def requires_translating_start():
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            translator_session_uuid = flask.request.cookies.get('translator_session')
            translation_uuid = flask.request.cookies.get('translation')

            if translator_session_uuid and translation_uuid:
                translator_session = TranslatorSession.query.join(
                    TranslatorSession.translator
                ).options(
                    contains_eager(TranslatorSession.translator)
                ).filter(
                    TranslatorSession.activated_time.isnot(None),
                    TranslatorSession.uuid == str(translator_session_uuid)
                ).first()

                if translator_session:
                    translation = Translation.query.options(
                        joinedload(Translation.project),
                        joinedload(Translation.language),
                    ).filter(
                        Translation.uuid == str(translation_uuid)
                    ).first()

                    if translation:
                        return view(translator_session.translator, translation, *args, **kwargs)

            return flask.abort(403)

        return wrapped_view

    return decorator


@blueprint.route('/translator/get-translation')
@requires_translating_start()
def get_translation(translator, translation):
    return __get_translation__(translator, translation)


def __get_translation__(translator, translation):
    project = translation.project

    language = translation.language
    language_plural_forms = language.plural_forms

    strings = project.strings_query.outerjoin(
        Suggestion, (String.id == Suggestion.string_id) & (Suggestion.translation == translation)
    ).options(
        contains_eager(String.suggestions)
    ).order_by(
        String.position,
        Suggestion.votes_value.desc(),
        Suggestion.added_time,
    )

    # TODO: select only the suggestions made in this translation
    voted_suggestions = set(result[0] for result in SuggestionVote.query.filter(SuggestionVote.translator == translator).values(SuggestionVote.suggestion_id))

    def _as_suggestion_data(suggestion, plural_forms=None):
        suggestion_data = dict(
            value={plural_form: suggestion.get_value(plural_form) for plural_form in plural_forms} if plural_forms else suggestion.value_other,
            votes=suggestion.votes_value,
        )
        if suggestion.id in voted_suggestions:
            suggestion_data['voted'] = True
        return suggestion_data

    strings_data = []
    for string in strings:
        string_data = dict(
            name=string.name,
        )
        if string.markers:
            string_data['markers'] = json.loads(string.markers)
        string_data.update(dict(
            value=dict(one=string.value_one, other=string.value_other) if string.value_one else string.value_other,
        ))
        suggestions_data = string_data['suggestions'] = []
        for suggestion in string.suggestions:
            suggestions_data.append(_as_suggestion_data(suggestion, plural_forms=language_plural_forms if string.value_one else None))

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


@blueprint.route('/translator/add-suggestion', methods=['POST'])
@requires_translating_start()
def add_suggestion(translator_session_uuid, translation_uuid):
    translator_session = TranslatorSession.query.join(
        TranslatorSession.translator
    ).options(
        contains_eager(TranslatorSession.translator)
    ).filter(
        TranslatorSession.activated_time.isnot(None),
        TranslatorSession.uuid == str(translator_session_uuid),
    ).first()
    if not translator_session:
        return flask.abort(404)

    translator = translator_session.translator

    translation = Translation.query.options(
        joinedload(Translation.project),
        joinedload(Translation.language),
    ).filter(
        Translation.uuid == str(translation_uuid),
    ).first()
    if not translation:
        return flask.abort(404)

    project = translation.project

    string_name = flask.request.json.get('string')
    suggestion_plural_form = flask.request.json.get('plural_form')
    suggestion_value = flask.request.json.get('value')
    if not string_name or not suggestion_plural_form or not suggestion_value:
        return flask.abort(400)

    string = String.query.filter(String.name == string_name, String.project == project).first()
    if not string:
        return flask.abort(404)

    if string.value_one:
        if suggestion_plural_form not in translation.language.plural_forms:
            return flask.abort(400)
    elif suggestion_plural_form != 'other':
        return flask.abort(400)

    suggestion = Suggestion.query.filter(
        Suggestion.translation == translation,
        Suggestion.string == string,
        Suggestion.plural_form == suggestion_plural_form,
        Suggestion.value == suggestion_value,
    ).first()
    if not suggestion:
        suggestion = Suggestion(
            translation=translation,
            translator=translator,
            string=string,
            plural_form=suggestion_plural_form,
            value=suggestion_value,
        )
        db.session.add(suggestion)
        db.session.flush()

    SuggestionVote.query.filter(
        SuggestionVote.id.in_(
            db.session.query(
                SuggestionVote.id
            ).join(
                SuggestionVote.suggestion
            ).join(
                Suggestion.string
            ).filter(
                String.id == string.id,
                Suggestion.translation == translation,
                Suggestion.plural_form == suggestion_plural_form,
                SuggestionVote.translator == translator,
            ).subquery()
        )
    ).delete(synchronize_session=False)

    db.session.add(SuggestionVote(
        suggestion=suggestion,
        translator=translator,
    ))

    db.session.commit()

    return __get_translation__(translator, translation)
