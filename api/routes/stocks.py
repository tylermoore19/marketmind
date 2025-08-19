from clients.GeminiClient import GeminiClientError
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from utils.helpers import create_error_response
from google import genai
from datetime import date
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
        return jsonify({'data': top_stocks}), 200
        # raise Exception("Simulated error for testing")
    except Exception as e:
        return jsonify(create_error_response('Failed to fetch top stocks', 'fetch_error')), 500

@stocks_bp.route('/generate_content', methods=['GET'])
@jwt_required()
def generate_content():
    try:
        client = current_app.config['GEMINI_CLIENT']
        response = client.get_top_sport_picks(date.today().strftime('%Y-%m-%d'))
        
        print('response', response)
        
        return jsonify({'data': response}), 200
    except GeminiClientError as e:
        print(f'Gemini API error: {e}')
        return jsonify(create_error_response('Failed to generate content', 'gemini_error')), 503
    except Exception as e:
        print(f'Unexpected error: {e}')
        return jsonify(create_error_response('Internal server error', 'internal_error')), 500