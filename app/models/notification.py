from ..extensions import db
from .base import Base

class Notification(Base):
    __tablename__ = 'notifications'
    receiver = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False)

    user_notifications = db.relationship("User", back_populates="notifications")