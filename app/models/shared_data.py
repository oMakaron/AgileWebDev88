from datetime import datetime, timezone
from .base import Base  
from ..extensions import db


class SharedData(Base):
    __tablename__ = 'shared_data'

    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    shared_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    chart = db.relationship("Chart", backref="shared_entries", lazy=True)
    shared_with_user = db.relationship("User", foreign_keys=[shared_with_user_id])
    shared_by_user = db.relationship("User", foreign_keys=[shared_by_user_id])
