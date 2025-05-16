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

    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),    primary_key=True)

    chart = db.relationship('Chart', back_populates='shared_with')
    user  = db.relationship('User',  back_populates='shared_charts')
