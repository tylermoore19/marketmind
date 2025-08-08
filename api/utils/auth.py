from functools import wraps
from utils.helpers import create_error_response
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify(create_error_response('Invalid token', 'invalid_token')), 401
    return decorated

def get_current_user_id():
    return get_jwt_identity()
