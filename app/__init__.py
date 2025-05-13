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
        from app.models import User, File, Chart, SharedFile, SharedChart
        from app.routes import bp
        from app.api import api as api_blueprint

        app.register_blueprint(bp)
        app.register_blueprint(api_blueprint)

        from app.api import files, charts, plots
        app.register_blueprint(files)
        app.register_blueprint(charts)
        app.register_blueprint(plots)


    return app


def cli_app():
    return create_app(DeploymentConfig)
