import click
from flask import Flask
from flask_graphql import GraphQLView

import commands
from models import db_session
from schema import schema
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.debug = True


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

if __name__ == '__main__':
    app.run()
