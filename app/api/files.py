from flask import Blueprint, jsonify, request, session
from app.models import File
from app.extensions import db

file_api = Blueprint('file_api', __name__, url_prefix='/files')

def require_user():
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({'error': 'Unauthorized'}), 401
    return user_id, None, None

@file_api.route('/files', methods=['GET'])
def list_files():
    user_id, error, status = require_user()
    if error: return error, status
    files = File.query.filter_by(owner_id=user_id).all()
    return jsonify([{'id': f.id, 'name': f.name} for f in files])

@file_api.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    user_id, error, status = require_user()
    if error: return error, status
    file = File.query.get_or_404(file_id)
    if file.owner_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({'id': file.id, 'name': file.name})

@file_api.route('/files', methods=['POST'])
def create_file():
    user_id, error, status = require_user()
    if error: return error, status
    data = request.json
    file = File(name=data['name'], owner_id=user_id)
    db.session.add(file)
    db.session.commit()
    return jsonify({'id': file.id, 'name': file.name}), 201

@file_api.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id, error, status = require_user()
    if error: return error, status
    file = File.query.get_or_404(file_id)
    if file.owner_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(file)
    db.session.commit()
    return jsonify({'status': 'deleted'})
