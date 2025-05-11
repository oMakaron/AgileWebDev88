from flask import Blueprint, Response


files = Blueprint('files', __name__)


@files.route('/', methods=["GET"])
def get_all_files() -> Response:
    ...


@files.route('/', methods=["POST"])
def make_new_file() -> Response:
    ...


@files.route('/<int:file_id>/', methods=["GET"])
def get_file(file_id: int) -> Response:
    ...


@files.route('/<int:file_id>/', methods=["PUT"])
def edit_file(file_id: int) -> Response:
    ...

