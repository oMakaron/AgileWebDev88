from flask import url_for
from ..extensions import db
from .base import Base

class Chart(Base):
    __tablename__ = 'charts'

    name       = db.Column(db.String(255), nullable=False)
    owner_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id    = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    spec       = db.Column(db.Text,    nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

    owner = db.relationship('User', back_populates='charts')
    file  = db.relationship('File', back_populates='charts')

    shared_with = db.relationship('SharedChart', back_populates='chart', cascade='all, delete-orphan')

    @property
    def image_url(self):
        if not self.image_path:
            return None
        return url_for('static', filename=f'chart_images/{self.image_path}')
