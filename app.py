import logging

import click
import flask
from flask_graphql import GraphQLView
from flask_mail import Mail

import commands
from localizappion.registration import registration
from models import db_session
from schema import schema

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = flask.Flask(__name__)
app.config.from_object('settings.Config')
app.debug = True

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

if __name__ == '__main__':
    app.run()
