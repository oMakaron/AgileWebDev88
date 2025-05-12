from ..extensions import db
from .base import Base

class Notifications(Base):
    __tablename__ = 'notifications'
    chart_share = db.Column(db.Integer, db.ForeignKey('shared_charts.id'), nullable=True)
    file_share = db.Column(db.Integer, db.ForeignKey('shared_files.id'), nullable=True)
    follower = db.Column(db.Integer, db.ForeignKey('follows.id'), nullable=True)
    message = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False)

    chart_notifications = db.relationship("SharedChart", back_populates="notifications")
    file_notifications = db.relationship("SharedFile", back_populates="notifications")
    follow_notification = db.relationship("Follows", back_populates="notifications")