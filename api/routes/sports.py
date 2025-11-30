from clients.GeminiClient import GeminiClientError
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from utils.helpers import error_response, ok_response
from google import genai
from datetime import date

sports_bp = Blueprint('sports', __name__)

@sports_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_sport_predictions():
    try:
        client = current_app.config['GEMINI_CLIENT']
        response = client.get_top_sport_picks(date.today().strftime('%Y-%m-%d'))
        # response = client.get_top_sport_picks('2025-08-24')
        
        print('response', response)

        return jsonify(ok_response(response)), 200
    except GeminiClientError as e:
        print(f'Gemini API error: {e}')
        return jsonify(error_response('Failed to generate content', 'gemini_error')), 503
    except Exception as e:
        print(f'Unexpected error: {e}')
        return jsonify(error_response('Internal server error', 'internal_error')), 500