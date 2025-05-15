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
        from app.models import User, File, Chart, SharedFile, SharedChart, Notification, Friend

        from app.routes import bp
        app.register_blueprint(bp)

        from app.api import files, charts, plots, friends, notifications
        app.register_blueprint(files, url_prefix='/files')
        app.register_blueprint(charts, url_prefix='/charts')
        app.register_blueprint(plots, url_prefix='/plots')
        app.register_blueprint(friends, url_prefix='/friends')
        app.register_blueprint(notifications, url_prefix='/notifications')

    return app


def cli_app():
    return create_app(DeploymentConfig)
