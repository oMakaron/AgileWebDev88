from ..extensions import db


class SharedFile(db.Model):
    __tablename__ = 'shared_files'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), primary_key=True)

    # Set to either `view` or `edit`
    privilege = db.Column(db.String(5), nullable=False)

    user = db.relationship('User', back_populates='shared_files')
    file = db.relationship('File', back_populates='shared_with')
    notifications = db.relationship("Notifications", back_populates="chart_notifications")


class SharedChart(db.Model):
    __tablename__ = 'shared_charts'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), primary_key=True)

    # Set to either `view` or `edit`
    privilege = db.Column(db.String(5), nullable=False)

    user = db.relationship('User', back_populates='shared_charts')
    chart = db.relationship('Chart', back_populates='shared_with')
    notifications = db.relationship("Notifications", back_populates="file_notifications")
