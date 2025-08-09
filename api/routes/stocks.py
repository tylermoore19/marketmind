from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models import User
from utils.helpers import create_error_response
import time

stocks_bp = Blueprint('stocks', __name__)

@stocks_bp.route('/top', methods=['GET'])
@jwt_required()
def get_top_stocks():
    try:
        # Fetch top stocks logic here
        # This is a placeholder for actual stock fetching logic
        top_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 150.00},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 2800.00},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": 3400.00}
        ]

        time.sleep(3)
        return jsonify(top_stocks), 200
        # raise Exception("Simulated error for testing")
    except Exception as e:
        return jsonify(create_error_response('Failed to fetch top stocks', 'fetch_error')), 500
    
@stocks_bp.route('/testing', methods=['GET'])
@jwt_required()
def get_testing():
    try:
        time.sleep(6)
        return jsonify({"this is a test": "ok"}), 200
        # raise Exception("Simulated error for testing")
    except Exception as e:
        return jsonify(create_error_response('Failed to fetch top stocks', 'fetch_error')), 500