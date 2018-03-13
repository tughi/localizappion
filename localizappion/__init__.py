import flask
from flask_graphql import GraphQLView
from flask_mail import Mail
from flask_migrate import Migrate

app = flask.Flask(__name__)
app.config.from_object('settings.Config')

Mail().init_app(app)

from localizappion.models import db

Migrate(app, db)

from localizappion import admin
from localizappion import registration
from localizappion import translator
from localizappion.api import translation
from localizappion.schema import schema

app.add_url_rule(
    '/graphql',
    view_func=admin.requires_admin()(
        GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=app.config['DEBUG'],
        )
    )
)

app.register_blueprint(admin.blueprint)
app.register_blueprint(registration.blueprint)
app.register_blueprint(translator.blueprint)
app.register_blueprint(translation.blueprint, url_prefix='/api')
