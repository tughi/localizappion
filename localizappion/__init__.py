import flask
from flask_graphql import GraphQLView
from flask_mail import Mail

app = flask.Flask(__name__)
app.config.from_object('settings.Config')

Mail().init_app(app)

from localizappion import admin
from localizappion import registration
from localizappion.api import translation
from localizappion.api import translators
from localizappion.schema import schema

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=app.config['DEBUG'],
    )
)

app.register_blueprint(admin.blueprint)
app.register_blueprint(registration.blueprint)
app.register_blueprint(translators.blueprint, url_prefix='/api')
app.register_blueprint(translation.blueprint, url_prefix='/api')
