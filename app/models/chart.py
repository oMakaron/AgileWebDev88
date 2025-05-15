from ..extensions import db
from .base import Base
from .associations import SharedChart

class Chart(Base):
    __tablename__ = 'charts'

    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    spec = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

    shared_with = db.relationship('SharedChart', back_populates='chart')