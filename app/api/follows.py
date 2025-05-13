from flask import Blueprint, Response, jsonify, request

from .utils import require_login, get_user
from ..extensions import db
from ..models import User, Follows

follows = Blueprint('follows', __name__)

@follows.route('/')
@require_login
def get_follows() -> Response: 
    type = request.args.get('type')
    user_id = get_user()
    user = User.query.get_or_404(user_id)
    follow_dict = {'followers': user.followers, 'following': user.following}
    
    if(type):
        try:
            return jsonify(follow_dict[type])
        except KeyError:
            response = jsonify({'error': 'Invalid type argument'})
            response.status_code = 400
            return response
    else:
        return jsonify(follow_dict)

@follows.route('/<int:target_id>', methods=["POST"])
@require_login
def follow(target_id) -> Response:
    try:
        if (Follows.query.filter_by(follower=get_user(), following=target_id).first()):
            response = jsonify({'error': 'Person already followed'})
            response.status_code = 409
            return response
        follows = Follows(follower=get_user(), following=target_id)
        db.session.add(follows)
        db.session.commit()

        response = jsonify({'id': follows.id})
        response.status_code = 201
        return response

    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response
    
@follows.route('/<int:target_id>', methods=["DELETE"])
@require_login
def unfollow(target_id) -> Response:
    follow = Follows.query.filter_by(follower=get_user(), following=target_id).first_or_404()
    
    try:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'message': 'User unfollowed.'})
    
    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response   
