import logging

import flask
from flask_graphql import GraphQLView
from flask_mail import Mail

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = flask.Flask(__name__)
app.config.from_object('settings.Config')

Mail().init_app(app)

from .schema import schema
from .registration import registration

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,
    )
)

app.register_blueprint(registration)
