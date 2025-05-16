from ..extensions import db
from .base import Base
from datetime import datetime, timezone

class Notification(Base):
    __tablename__ = 'notification'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
