from os import path, remove

from flask import Blueprint, Response, abort, jsonify, request

from ..models import File
from ..extensions import db
from .utils import require_login, get_user, UPLOADS_FOLDER


files = Blueprint('files', __name__)


@files.route('/', methods=["GET"])
@require_login
def get_all_files() -> Response:
    files = File.query.filter_by(owner_id=get_user()).all()
    return jsonify([{'id': file.id, 'name': file.name} for file in files])


@files.route('/', methods=["POST"])
@require_login
def make_new_file() -> Response:
    file = request.files.get('file')
    name = request.form.get('name')

    if not (file and name):
        abort(400, desctiption="Missing required fields.")

    try:
        file_data = file.read()
        new_file = File(name=name, owner_id=get_user(), data = file_data) # type: ignore
        db.session.add(new_file)
        db.session.commit()

        response = jsonify({'id': new_file.id})
        response.status_code = 201

        return response

    except Exception:
        db.session.rollback()
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response


@files.route('/<int:file_id>/', methods=["GET"])
@require_login
def get_file(file_id: int) -> Response:
    file = File.query.get_or_404(file_id)

    if file.owner_id != get_user() and not any(share.user_id == get_user() for share in file.shared_with):
        abort(403, description="You do not have access to this file.")

    try:
        content = file.data
        return Response(content, mimetype='text/csv')

    except Exception:
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response


@files.route('/<int:file_id>/', methods=["PUT"])
@require_login
def edit_file(file_id: int) -> Response:
    file = File.query.filter_by(id=file_id, owner_id=get_user()).first_or_404()

    new_name = request.form.get('name')
    new_file = request.files.get('file')

    try:
        if new_name:
            file.name = new_name
        if new_file:
            new_file_data = new_file.read()
            file.data = new_file_data

        db.session.commit()
        return jsonify({'message': 'File updated successfully.'})

    except Exception:
        db.session.rollback()

        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response



@files.route('/<int:file_id>/', methods=["DELETE"])
@require_login
def delete_file(file_id: int) -> Response:
    file = File.query.filter_by(id=file_id, owner_id=get_user()).first_or_404()

    try:
        db.session.delete(file)
        db.session.commit()

        return jsonify({'message': 'File deleted successfully.'})

    except Exception:
        db.session.rollback()

        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response

