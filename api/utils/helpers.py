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
    """
    Extract a JSON object or array from a text blob.

    Behavior:
    - If a fenced ```json block exists, return the parsed JSON inside it.

    Returns the parsed Python object (dict or list).
    """
    # Try to find a fenced ```json block first
    fenced_match = re.search(r'```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```', text, re.IGNORECASE)
    if fenced_match:
        json_str = fenced_match.group(1)
        try:
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Found fenced JSON but failed to parse: {e}")

    raise ValueError("Reached end of text while searching for end of JSON object/array")