from flask import Blueprint, Response, jsonify
from sqlalchemy import event

from ..models import Notification, SharedChart, SharedFile, Follows, User, Chart, File
from .utils import require_login, get_user
from ..extensions import db

notifications = Blueprint('notifications', __name__)

#get notifs
#mark as read
#create a trigger

@event.listens_for(SharedChart, 'after_update')
def chart_notif(mapper, connection, target):
    connection.execute(
        Notification.__table__.insert(), 
        {'receiver': target.user_id,
         'message': f'{User.query.filter_by(id=target.user_id).first_or_404().fullname} have shared you a chart, {Chart.query.filter_by(id=target.chart_id).first_or_404.name}!'}
    )

@event.listens_for(SharedFile, 'after_update')
def chart_notif(mapper, connection, target):
    connection.execute(
        Notification.__table__.insert(), 
        {'receiver': target.user_id,
         'message': f'{User.query.filter_by(id=target.user_id).first_or_404().fullname} have shared you a file, {File.query.filter_by(id=target.file_id).first_or_404.name}!'}
    )

@event.listens_for(Follows, 'after_update')
def chart_notif(mapper, connection, target):
    connection.execute(
        Notification.__table__.insert(), 
        {'receiver': target.following,
         'message': f'{User.query.filter_by(id=target.follower).first_or_404().fullname} is following you.'}
    )

@notifications.route('/', methods=['GET'])
@require_login
def get_notifs():
    notif = Notification.query.filter_by(receiver=get_user()).all()
    return jsonify([{'id': notifs.id, 'message': notifs.message} for notifs in notif])

@notifications.route('/<int:notif_id>', methods=['PATCH'])
@require_login
def mark_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id).first_or_404()
    try:
        notif.read = False
        db.session.commit()
    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response   