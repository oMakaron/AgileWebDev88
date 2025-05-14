from flask import Blueprint, Response, jsonify, request

from .utils import require_login, get_user
from ..extensions import db
from ..models import User, Friend

friends = Blueprint('friends', __name__)

@friends.route('/')
@require_login
def get_friends() -> Response: 
    type = request.args.get('type')
    user_id = get_user()
    user = User.query.get_or_404(user_id)
    friend_dict = {'requested': Friend.query.filter_by(user_id=user.id, is_friend=False).all(), 
                   'requests': Friend.query.filter_by(friend_id=user.id, is_friend=False).all(), 
                   'friends': User.friends}
    
    if(type):
        try:
            return jsonify(friend_dict[type])
        except KeyError:
            response = jsonify({'error': 'Invalid type argument'})
            response.status_code = 400
            return response
    else:
        return jsonify(friend_dict)

@friends.route('/<int:target_id>/', methods=["POST"])
@require_login
def request_add(target_id) -> Response:
    try:
        if (Friend.query.filter_by(follower=get_user(), friend_id=target_id).first()):
            response = jsonify({'error': 'Person is already friend/requested'})
            response.status_code = 409
            return response
        friend_requested = Friend.query.filter_by(user_id=target_id, friend_id=get_user()).first()
        if(friend_requested):
            friend_requested.is_friend = True
            req = Friend(user_id=get_user(), friend_id=target_id, is_friend=True)
            db.session.add(req)
            db.session.commit()
        else:    
            req = Friend(user_id=get_user(), friend_id=target_id)
            db.session.add(req)
            db.session.commit()

        response = jsonify({'id': req.id})
        response.status_code = 201
        return response

    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response
    
@friends.route('/<int:target_id>/', methods=["DELETE"])
@require_login
def unfriend(target_id) -> Response:
    friend = Friend.query.filter_by(follower=get_user(), following=target_id).first_or_404()
    friend_user = Friend.query.filter_by(follower=target_id, following=get_user()).first()
    try:
        db.session.delete(friend)
        if friend_user:
            db.session.delete(friend_user)
        db.session.commit()
        response = jsonify({'message': 'User unfriended.'})
        response.status_code = 204
        return response
    
    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response   