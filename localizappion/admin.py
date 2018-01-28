from functools import wraps

import flask
from flask import render_template

from localizappion.utils import create_hash

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


def requires_admin():
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if create_hash(flask.session.get('username')) == flask.current_app.config['ADMIN_USERNAME']:
                return view(*args, **kwargs)
            return flask.redirect(flask.url_for('admin.login'))

        return wrapped_view

    return decorator


@blueprint.route('/admin/login', methods=('GET', 'POST'))
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get('username', '')
        password = flask.request.form.get('password', '')
        if create_hash(username) == flask.current_app.config['ADMIN_USERNAME'] and create_hash(password) == flask.current_app.config['ADMIN_PASSWORD']:
            flask.session['username'] = username
            return flask.redirect(flask.url_for('admin.index'))
    return render_template(
        'admin/login.html',
    )


@blueprint.route('/admin/logout')
def logout():
    flask.session['username'] = None
    return flask.redirect(flask.url_for('admin.login'))


@blueprint.route('/admin')
@requires_admin()
def index():
    return render_template(
        'admin/index.html',
    )
