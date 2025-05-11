from ..extensions import db
from .base import Base
from .associations import SharedFile


class File(Base):
    __tablename__ = 'files'

    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    shared_with = db.relationship('SharedFile', back_populates='file')
