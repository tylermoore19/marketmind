import json
import re


def create_error_response(error_message, code):
    """
    Returns a dict with 'message' and 'code' keys for consistent error responses.
    """
    return {'message': error_message, 'code': code}

def extract_json_array(text: str):
    """Regex: find 'json' then capture everything between the first [ and its matching ]"""
    match = re.search(r'json\s*(\[\s*{.*}\s*\])', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in text.")
    
    json_str = match.group(1)
    return json.loads(json_str)