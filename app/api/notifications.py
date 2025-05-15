from flask import Blueprint, Response, jsonify, request, url_for
from sqlalchemy import event, insert, delete

from ..models import Notification, SharedChart, SharedFile, Follows, User, Chart, File, Friend
from .utils import require_login, get_user
from ..extensions import db

notifications = Blueprint('notifications', __name__)

@event.listens_for(SharedChart, 'after_update')
def chart_notif(mapper, connection, target):
    notif = Notification.__table__
    chart = Chart.query.get(target.chart_id)
    sender = User.query.get(get_user())
    connection.execute(
        notif.insert().values(user_id=target.user_id,
                              message=f'{sender.fullname} have shared you a chart, {chart.name}',
                              href= url_for('routes.dashboard'))
    )

@event.listens_for(SharedChart, 'before_delete')
def chart_delete(mapper, connection, target):
    notif = Notification.__table__
    chart = Chart.query.get(target.chart_id)
    target_notif = Notification.query.filter(Notification.message.contains(chart.name)).first()
    try:
        connection.execute(
            notif.delete().where(notif.c.id == target_notif.id)
        )
    except Exception:
        pass

@event.listens_for(SharedFile, 'after_update')
def file_notif(mapper, connection, target):
    notif = Notification.__table__
    file = File.query.get(target.file_id)
    sender = User.query.get(get_user())
    try:
        connection.execute(
            notif.insert().values(user_id=target.user_id,
                                message=f'{sender.fullname} have shared you a file, {file.name}',
                                href= url_for('routes.dashboard'))
        )
    except Exception:
        pass

@event.listens_for(SharedFile, 'before_delete')
def file_delete(mapper, connection, target):
    notif = Notification.__table__
    file = File.query.get(target.file_id)
    target_notif = Notification.query.filter(Notification.message.contains(file.name)).first()
    try:
        connection.execute(
            notif.delete().where(notif.c.id == target_notif.id)
        )
    except Exception:
        pass

@event.listens_for(Friend, 'after_update')
def friend_notif(mapper, connection, target):
    notif = Notification.__table__
    friend = User.query.get(target.user_id)
    try:
        connection.execute(
            notif.insert().values(user_id=target.friend_id,
                                message=f'{friend.fullname} added you as their friend.',
                                href= url_for('routes.friends'))
        )
    except Exception:
        pass

@event.listens_for(Friend, 'before_delete')
def unfriend_notif(mapper, connection, target):
    notif = Notification.__table__
    if(target.is_friend):
        friend = User.query.get(target.user_id)
        try:
            connection.execute(
                notif.insert().values(user_id=target.friend_id,
                                      message=f'{friend.fullname} and you are no longer friends.',
                                      href= url_for('routes.friends'))
            )
        except Exception:
            pass

@notifications.route('/', methods=['GET'])
@require_login
def get_notifs():
    notif = Notification.query.filter_by(receiver=get_user()).all()
    return jsonify([{'id': notifs.id, 
                     'message': notifs.message, 
                     'href': notifs.href, 
                     'date': notifs.created_at, 
                     'is_read': notifs.is_read} for notifs in notif])

@notifications.route('/<int:notif_id>', methods=['PATCH'])
@require_login
def mark_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id).first_or_404()
    try:
        notif.is_read = True
        db.session.commit()
        response = jsonify({'message': 'notification read'})
        response.status_code = 200
        return response
    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response   