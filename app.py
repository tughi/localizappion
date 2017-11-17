import base64
import logging
from datetime import datetime
from hashlib import sha512

import click
import flask
from flask_graphql import GraphQLView
from flask_mail import Mail
from flask_mail import Message

import commands
from models import Project
from models import Translator
from models import TranslatorClient
from models import db_session
from schema import schema

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = flask.Flask(__name__)
app.config.from_object('settings.Config')
app.debug = True

mail = Mail(app)


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


@app.route('/translators/register', methods=['POST'])
def register_translator():
    registration = flask.request.json  # type: dict
    project_uuid = registration['project'] if 'project' in registration else ''
    email = registration['email'] if 'email' in registration else ''

    project = db_session.query(Project).filter(Project.uuid == project_uuid).first()
    if not project:
        return flask.abort(404)

    if len(email) < 3 or email.find('@', 1) < 0:
        return flask.jsonify(message='Invalid email address')

    email_hash = base64.standard_b64encode(sha512(email.encode()).digest()).decode()

    translator = db_session.query(Translator).filter(Translator.email_hash == email_hash).first()
    if not translator:
        translator = Translator(email_hash=email_hash)
        db_session.add(translator)

    translator_client = TranslatorClient(translator=translator)
    db_session.add(translator_client)
    db_session.commit()

    message = Message(
        subject="New {0} translator".format(project.name),
        sender=app.config['REGISTRATION_MAIL_SENDER'],
        recipients=[email],
        html=
        """
            <p>
                Please <a href="{1}">click here</a> to confirm your email address and complete your request
                in becoming a translator for <b>{0}</b>.
            </p>
            <p>
                If you received this email by mistake or weren't expecting it, please ignore it.
            </p>
            <p>
                Cheers,<br>
                Tughi
            </p>
        """.format(project.name, flask.url_for('activate_translator', translator_client=translator_client.uuid, _external=True)),
    )
    mail.send(message)

    return flask.jsonify(message="You will receive shortly an activation email", translator_client=translator_client.uuid)


@app.route('/translators/<uuid:translator_client>/activate')
def activate_translator(translator_client=None):
    translator_client = db_session.query(TranslatorClient).filter(TranslatorClient.uuid == str(translator_client)).first()
    if not translator_client:
        # TODO: render template
        return flask.abort(404)

    if not translator_client.activated_time:
        translator_client.activated_time = datetime.now()
        db_session.commit()

    # TODO: render template
    return flask.jsonify(message="Thanks for becoming a translator.")


if __name__ == '__main__':
    app.run()
