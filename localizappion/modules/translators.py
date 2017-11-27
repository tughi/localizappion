import base64
from datetime import datetime
from hashlib import sha512

import flask
from flask_mail import Message

from ..models import Project
from ..models import Translator
from ..models import TranslatorSession
from ..models import db

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


def create_email_hash(email):
    hash_data = '{0}+{1}'.format(email, flask.current_app.config['REGISTRATION_MAIL_SENDER'])
    return base64.standard_b64encode(sha512(hash_data.encode()).digest()).decode()


@blueprint.route('/register', methods=['POST'])
def register():
    request_data = flask.request.json  # type: dict

    project_uuid = request_data['project'] if 'project' in request_data else ''
    project = db.session.query(Project).filter(Project.uuid == project_uuid).first()
    if not project:
        return flask.abort(404)

    email = request_data['email'] if 'email' in request_data else ''
    if len(email) < 3 or email.find('@', 1) < 0:
        return flask.jsonify(message='Invalid email address')

    email_hash = create_email_hash(email)

    translator = db.session.query(Translator).filter(Translator.email_hash == email_hash).first()
    if not translator:
        translator = Translator(email_hash=email_hash)
        db.session.add(translator)

    translator_session = TranslatorSession(translator=translator)
    db.session.add(translator_session)
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
        """.format(project.name, flask.url_for('.activate', activation_code=translator_session.activation_code, _external=True)),
    )

    flask.current_app.extensions.get('mail').send(message)

    return flask.jsonify(message="You will receive shortly an activation email", translator_client=translator_session.uuid)


@blueprint.route('/activate/<uuid:activation_code>')
def activate(activation_code=None):
    translator_session = TranslatorSession.query.filter(TranslatorSession.activation_code == str(activation_code)).first()
    if not translator_session:
        # TODO: render template
        return flask.abort(404)

    if not translator_session.activated_time:
        translator_session.activated_time = datetime.now()
        db.session.commit()

    # TODO: render template
    return flask.jsonify(message="Thanks for becoming a translator.")
