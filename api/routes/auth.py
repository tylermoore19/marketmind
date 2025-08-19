from flask import Blueprint, request, jsonify
from app import db
from models import User
from utils.validators import validate_email
from utils.helpers import error_response, ok_response

auth_bp = Blueprint('auth', __name__)

# Error responses
INVALID_CREDENTIALS = error_response('Invalid email or password', 'invalid_credentials')
MISSING_FIELDS = error_response('Missing required fields', 'missing_fields')
INVALID_EMAIL = error_response('Invalid email format', 'invalid_email')
EMAIL_EXISTS = error_response('Email already registered', 'email_exists')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['email', 'password']):
        return jsonify(MISSING_FIELDS), 400
    
    # Validate email format
    if not validate_email(data['email']):
        return jsonify(INVALID_EMAIL), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify(EMAIL_EXISTS), 409
    
    # Create new user
    try:
        user = User(email=data['email'])
        user.password = data['password']  # This will hash the password
        db.session.add(user)
        db.session.commit()
        
        # Generate auth token
        token = user.generate_auth_token()
        
        return jsonify(ok_response({'token': token}, 'User registered successfully')), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(error_response('Registration failed', 'registration')), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['email', 'password']):
        return jsonify(MISSING_FIELDS), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Verify user exists and password is correct
    if user and user.verify_password(data['password']):
        token = user.generate_auth_token()
        return jsonify(ok_response({'token': token, 'user': {'id': user.id, 'email': user.email}}, 'Login successful')), 200
    
    # Always return 401 Unauthorized for invalid credentials
    return jsonify(INVALID_CREDENTIALS), 401
