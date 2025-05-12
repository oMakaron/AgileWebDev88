from os import abort, path, remove

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
        abort(400, desctiption="Missing required fiels.")

    try:
        new_file = File(name=name, owner_id=get_user()) # type: ignore
        db.session.add(new_file)
        db.session.commit()

        file_name = f"{new_file.id}.csv"
        file_path = path.join(UPLOADS_FOLDER, file_name)

        file.save(file_path)

        response = jsonify({'id': new_file.id})
        response.status_code = 201

        return response

    except:
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

    file_path = path.join(UPLOADS_FOLDER, f"{file_id}.csv")
    if not path.exists(file_path):
        response = jsonify({'error': 'File content is missing.'})
        response.status_code = 404
        return response

    try:
        with open(file_path, "r") as file:
            content = file.read()
        return Response(content, mimetype='text/csv')

    except:
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
            file_path = path.join(UPLOADS_FOLDER, f"{file_id}.csv")
            new_file.save(file_path)

        db.session.commit()
        return jsonify({'message': 'File updated successfully.'})

    except:
        db.session.rollback()

        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response



@files.route('/<int:file_id>/', methods=["DELETE"])
@require_login
def delete_file(file_id: int) -> Response:
    file = File.query.filter_by(id=file_id, owner_id=get_user()).first_or_404()

    file_path = path.join(UPLOADS_FOLDER, f"{file_id}.csv")

    try:
        if path.exists(file_path):
            remove(file_path)

        db.session.delete(file)
        db.session.commit()

        return jsonify({'message': 'File deleted successfully.'})

    except:
        db.session.rollback()

        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response

