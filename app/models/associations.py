from ..extensions import db
from .base import Base

class SharedFile(Base):
    __tablename__ = 'shared_files'

    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    file = db.relationship('File', back_populates='shared_with')
    user = db.relationship('User', back_populates='shared_files')


class SharedChart(Base):
    __tablename__ = 'shared_charts'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), nullable=False)

    privilege = db.Column(db.String(5), nullable=False)

    user = db.relationship('User', back_populates='shared_charts')
    chart = db.relationship('Chart', back_populates='shared_with')

