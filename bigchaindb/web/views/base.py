"""
Common classes and methods for API handlers
"""
import logging

from flask import jsonify, request

logger = logging.getLogger(__name__)


def make_error(status_code, message=None):
    if status_code == 404 and message is None:
        message = 'Not found'
    response_content = {'status': status_code, 'message': message}
    logger.error('HTTP API error: %(status)s - %(message)s', response_content)
    response = jsonify(response_content)
    response.status_code = status_code
    return response


def base_url():
    return '%s://%s/' % (request.environ['wsgi.url_scheme'],
                         request.environ['HTTP_HOST'])
