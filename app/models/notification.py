from ..extensions import db
from .base import Base

class Notification(Base):
    __tablename__ = 'notification'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    href = db.Column(db.String(255), nullable=True)