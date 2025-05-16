from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from .base import Base

class User(Base):
    __tablename__ = 'users'

    fullname = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # owns many files & charts
    files  = db.relationship('File',  back_populates='owner',   cascade='all, delete-orphan')
    charts = db.relationship('Chart', back_populates='owner',  cascade='all, delete-orphan')

    # shared associations
    shared_files  = db.relationship('SharedFile',  back_populates='user', cascade='all, delete-orphan')
    shared_charts = db.relationship('SharedChart', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)
