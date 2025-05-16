from ..extensions import db
from .base import Base

class File(Base):
    __tablename__ = 'files'

    name     = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationship back to User
    owner = db.relationship('User', back_populates='files')

    # a file can have many charts
    charts = db.relationship('Chart', back_populates='file', cascade='all, delete-orphan')

    # and be shared to many users
    shared_with = db.relationship('SharedFile', back_populates='file', cascade='all, delete-orphan')
