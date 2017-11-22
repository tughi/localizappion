import flask
from flask_graphql.graphqlview import GraphQLView
from sqlalchemy.orm import joinedload

from .schema import schema
from ...models import Translation

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)

graphql_view = GraphQLView(schema=schema, graphiql=True)


@blueprint.route('/api/v1/translations/<uuid:translation_uuid>/graphql', methods=('GET', 'POST'))
def graphql(translation_uuid):
    flask.request.translation = Translation.query \
        .options(joinedload(Translation.project), joinedload(Translation.language)) \
        .filter(Translation.uuid == str(translation_uuid)) \
        .first()
    return graphql_view.dispatch_request()
