from app.extensions import db
from .base import Base

class Friend(Base):
    __tablename__ = 'friend'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # prevent add one friend twice
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)