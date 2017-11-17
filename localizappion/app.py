import logging

import click
import flask
from flask_graphql import GraphQLView
from flask_mail import Mail

from . import commands
from .models import db_session
from .registration import registration
from .schema import schema

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = flask.Flask(__name__)
app.config.from_object('settings.Config')

mail = Mail()
mail.init_app(app)


@app.cli.command()
def init_db():
    click.echo("Init the database")
    commands.init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,
    )
)

app.register_blueprint(registration)
