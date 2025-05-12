from ..extensions import db
from .base import Base

class follows(Base):
    follower = db.Column(db.Integer, db.ForeignKey('users.id'))
    following = db.Column(db.Integer, db.ForeignKey('users.id'))