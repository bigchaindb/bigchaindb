from flask import jsonify


def make_error(status_code, message=None):

    if status_code == 404 and message is None:
        message = 'Not found'

    response = jsonify({
        'status': status_code,
        'message': message
    })
    response.status_code = status_code
    return response

