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

def extract_json_array(text):
    # Find the first JSON array in the text (even if surrounded by markdown)
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Found array but failed to parse JSON: {e}")
    raise ValueError("No JSON array found in text")