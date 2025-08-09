from utils.helpers import create_error_response
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt_identity, create_access_token
from os import environ
from dotenv import load_dotenv
from datetime import timedelta
from config import Config

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = environ.get('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify(create_error_response('Token has expired', 'token_expired')), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(create_error_response('Invalid token', 'invalid_token')), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(create_error_response('Authorization token is missing', 'authorization_required')), 401

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'sqlite:///marketmind.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.trips import trips_bp
    from routes.stocks import stocks_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(trips_bp, url_prefix='/api')
    app.register_blueprint(stocks_bp, url_prefix='/stocks')

    # Register routes
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to PlanVenture API"})

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"})

    @app.after_request
    def refresh_expiring_jwts(response):
        """Refresh JWT tokens if they are about to expire."""
        try:
            # Only refresh if the user is authenticated
            identity = get_jwt_identity()
            if identity:
                new_token = create_access_token(identity=identity)
                # You can send the new token in a custom header:
                response.headers['X-Refresh-Token'] = new_token
        except Exception:
            pass
        return response
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {
             "origins": Config.CORS_ORIGINS,
             "methods": Config.CORS_METHODS,
             "allow_headers": Config.CORS_HEADERS,
             "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS,
             "expose_headers": ["X-Refresh-Token"],
         }})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    
# TODO : create a new file that will take in a stock ticker, look up the fundamental data, use chatgpt to analyze it, and return the analysis
# this with the technical analysis should be enough to make a decision on whether to buy or sell the stock