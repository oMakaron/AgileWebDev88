from os import getenv, path

basedir = path.abspath(path.dirname(__file__))
default_db_location = 'sqlite:///' + path.join(basedir, 'app.db')


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = getenv('SECRET_KEY')


class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL') or default_db_location


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory"
    SECRET_KEY = "very-secret-key"
    WTF_CSRF_ENABLED = False
    TESTING = True
