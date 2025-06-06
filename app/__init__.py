from typing import Type

from flask import Flask
from config import Config, DeploymentConfig
from .extensions import db, migrate
from flask_moment import Moment
moment = Moment()


def create_app(configuration: Type[Config]) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configuration)

    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    with app.app_context():
        from app.models import User, File, Chart, SharedFile, SharedChart, Friend, Notification
        from app.routes import bp
        from app.api import api as api_blueprint

        app.register_blueprint(bp)
        app.register_blueprint(api_blueprint)

    return app


def cli_app():
    return create_app(DeploymentConfig)
