from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_
from sqlalchemy.orm import foreign

from ..extensions import db
from .base import Base
from .friend import Friend


class User(Base):
    __tablename__ = 'users'

    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    files = db.relationship('File', backref='owner')
    charts = db.relationship('Chart', backref='owner')

    shared_files = db.relationship('SharedFile', back_populates='user')
    shared_charts = db.relationship('SharedChart', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
