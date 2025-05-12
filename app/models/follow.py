from ..extensions import db
from .base import Base

class Follows(Base):
    __tablename__ = 'follows'
    follower = db.Column(db.Integer, db.ForeignKey('users.id'))
    following = db.Column(db.Integer, db.ForeignKey('users.id'))

    follower_user = db.relationship("User", foreign_keys=[follower], back_populates="following")
    following_user = db.relationship("User", foreign_keys=[following], back_populates="followers")