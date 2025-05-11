from typing import Type

from flask import Flask
from config import Config, DeploymentConfig
from .extensions import db, migrate


def create_app(configuration: Type[Config]) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configuration)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import User, File, Chart, SharedFile, SharedChart

        from app.routes import bp
        app.register_blueprint(bp)

    return app
    
 def cli_app():
     return create_app(DeploymentConfig)
