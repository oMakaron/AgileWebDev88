from app.extensions import db

from .base import Base

class Friend(Base):
    __tablename__ = 'friends'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_friend = db.Column(db.Boolean, nullable=False, default=False)
    # prevent add one friend twice
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)

    request_user = db.relationship("User", foreign_keys=[user_id], back_populates="requested")
    requested_user = db.relationship("User", foreign_keys=[friend_id], back_populates="requests")