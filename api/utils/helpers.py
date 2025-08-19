import json
import re


def error_response(error_message, code):
    """
    Returns a dict with 'message' and 'code' keys for consistent error responses.
    """
    return {'message': error_message, 'code': code}

def ok_response(data, message = None):
    """
    Returns a dict with 'message' and 'data' keys for consistent success responses.
    """
    response = {'data': data}
    if message:
        response['message'] = message
        
    return response

def extract_json_array(text: str):
    """Regex: find 'json' then capture everything between the first [ and its matching ]"""
    match = re.search(r'json\s*(\[\s*{.*}\s*\])', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in text.")
    
    json_str = match.group(1)
    return json.loads(json_str)