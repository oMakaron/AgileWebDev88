from flask import Flask
from flask_wtf.csrf import generate_csrf, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import os
from app.model import db

basedir = os.path.abspath(os.path.dirname(__file__))


# Tell Flask where to find the static folder
app = Flask(
    __name__,
    static_folder='../static',
    template_folder='templates'
)

app.secret_key = 'very-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) 
csrf = CSRFProtect(app)

from app import routes, model

