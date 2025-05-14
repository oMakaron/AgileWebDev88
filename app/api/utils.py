from os import path
from functools import wraps
from typing import Callable

from flask import session, jsonify


UPLOADS_FOLDER = path.join("app", "uploads")

def require_login(function: Callable) -> Callable:
    @wraps(function)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            response = jsonify({'error': 'must be logged in.'})
            response.status_code = 401
            return response
        return function(*args, **kwargs)

    return inner


def get_user() -> int:
    return session['user_id']