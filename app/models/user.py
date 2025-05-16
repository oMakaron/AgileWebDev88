from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from .base import Base

class User(Base):
    __tablename__ = 'users'

    fullname = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # owns many files & charts
    files  = db.relationship('File',  back_populates='owner',   cascade='all, delete-orphan')
    charts = db.relationship('Chart', back_populates='owner',  cascade='all, delete-orphan')

    # shared associations
    shared_files  = db.relationship('SharedFile',  back_populates='user', cascade='all, delete-orphan')
    shared_charts = db.relationship('SharedChart', back_populates='user', cascade='all, delete-orphan')

    requests = db.relationship('Friend', foreign_keys="Friend.user_id", back_populates='request_user', cascade='all,delete-orphan')
    requested = db.relationship('Friend', foreign_keys="Friend.friend_id", back_populates='requested_user', cascade='all, delete-orphan')

    shared_by_you = db.relationship('SharedData', foreign_keys='SharedData.shared_by_user_id', back_populates="shared_by_user", cascade='all, delete-orphan')
    shared_with_you = db.relationship('SharedData', foreign_keys='SharedData.shared_with_user_id', back_populates="shared_with_user", cascade='all, delete-orphan')

    notifications = db.relationship("Notification", back_populates="user_notifications", cascade='all, delete-orphan')

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)
