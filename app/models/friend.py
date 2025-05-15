from app.extensions import db

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_friend = db.Column(db.Boolean, nullable=False, default=False)
    # prevent add one friend twice
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'))