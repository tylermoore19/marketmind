from functools import wraps
from utils.helpers import create_error_response
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User

def auth_middleware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Check if user still exists in database
            user = User.query.get(current_user_id)
            if not user:
                return jsonify(create_error_response('User not found', 'user_not_found')), 401

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify(create_error_response('Invalid or expired token', 'invalid_token')), 401
    return decorated
