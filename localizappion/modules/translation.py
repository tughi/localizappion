import flask
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case
from sqlalchemy.sql.functions import sum

from localizappion.models import Language
from localizappion.models import Project
from localizappion.models import String
from localizappion.models import Suggestion
from localizappion.models import Translation
from localizappion.models import db

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


@blueprint.route('/api/v1/projects/<uuid:project_uuid>/translations/<string:language_code>/status')
def translation_status(project_uuid, language_code):
    translation = Translation.query \
        .join(Translation.project, Translation.language) \
        .options(joinedload(Translation.project), joinedload(Translation.language)) \
        .filter(Project.uuid == str(project_uuid)) \
        .filter(Language.code.in_((language_code.split('_')[0], language_code))) \
        .order_by(Language.code.desc()) \
        .first()
    if not translation:
        return flask.abort(404)

    required_strings = db.session \
        .query(sum(case([(String.value_one.isnot(None), len(translation.language.plural_forms))], else_=1))) \
        .filter(String.project == translation.project) \
        .scalar()

    translated_strings = db.session.query(Suggestion.string_id, Suggestion.plural_form) \
        .distinct() \
        .filter(Suggestion.translation == translation) \
        .filter(Suggestion.accepted.__eq__(True)) \
        .filter(Suggestion.votes_value > 0) \
        .count()

    return flask.jsonify(
        language_code=translation.language.code,
        language_name=translation.language.name,
        required_strings=required_strings,
        translated_strings=translated_strings,
    )
