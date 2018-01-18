import flask
from flask import render_template

blueprint = flask.Blueprint(__name__.split('.')[-1], __name__)


@blueprint.route('/admin')
def project_list():
    return render_template(
        'admin/index.html',
    )
