import base64
from datetime import datetime
from hashlib import sha512

import flask
from flask_mail import Message

from .models import Project
from .models import Translator
from .models import TranslatorClient
from .models import db

registration = flask.Blueprint(__name__.split('.')[-1], __name__)


def create_email_hash(email):
    hash_data = '{0}+{1}'.format(email, flask.current_app.config['REGISTRATION_MAIL_SENDER'])
    return base64.standard_b64encode(sha512(hash_data.encode()).digest()).decode()


@registration.route('/translators/register', methods=['POST'])
def register_translator():
    request_data = flask.request.json  # type: dict
    project_uuid = request_data['project'] if 'project' in request_data else ''
    email = request_data['email'] if 'email' in request_data else ''

    project = db.session.query(Project).filter(Project.uuid == project_uuid).first()
    if not project:
        return flask.abort(404)

    if len(email) < 3 or email.find('@', 1) < 0:
        return flask.jsonify(message='Invalid email address')

    email_hash = create_email_hash(email)

    translator = db.session.query(Translator).filter(Translator.email_hash == email_hash).first()
    if not translator:
        translator = Translator(email_hash=email_hash)
        db.session.add(translator)

    translator_client = TranslatorClient(translator=translator)
    db.session.add(translator_client)
    db.session.commit()

    message = Message(
        subject="New {0} translator".format(project.name),
        sender=flask.current_app.config['REGISTRATION_MAIL_SENDER'],
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
        """.format(project.name, flask.url_for('.activate_translator', translator_client=translator_client.uuid, _external=True)),
    )

    flask.current_app.extensions.get('mail').send(message)

    return flask.jsonify(message="You will receive shortly an activation email", translator_client=translator_client.uuid)


@registration.route('/translators/<uuid:translator_client>/activate')
def activate_translator(translator_client=None):
    translator_client = db.session.query(TranslatorClient).filter(TranslatorClient.uuid == str(translator_client)).first()
    if not translator_client:
        # TODO: render template
        return flask.abort(404)

    if not translator_client.activated_time:
        translator_client.activated_time = datetime.now()
        db.session.commit()

    # TODO: render template
    return flask.jsonify(message="Thanks for becoming a translator.")
