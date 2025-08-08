def create_error_response(error_message, code):
    """
    Returns a dict with 'message' and 'code' keys for consistent error responses.
    """
    return {'message': error_message, 'code': code}