from typing import Type

from flask import Flask
from config import Config, DeploymentConfig
from app.extensions import db, migrate


def create_app(configuration: Type[Config]) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configuration)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import User, File, Chart, SharedFile, SharedChart, Follows

        from app.routes import bp
        app.register_blueprint(bp)

        from app.api import files, charts, plots, follows
        app.register_blueprint(files, url_prefix='/files')
        app.register_blueprint(charts, url_prefix='/charts')
        app.register_blueprint(plots, url_prefix='/plots')
        app.register_blueprint(follows, url_prefix='/follows')


    return app


def cli_app():
    return create_app(DeploymentConfig)

