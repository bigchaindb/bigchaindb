# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from unittest.mock import Mock

OUTPUTS_ENDPOINT = '/api/v1/outputs/'


def test_middleware_does_nothing_when_no_content_type_is_provided():
    from bigchaindb.web.strip_content_type_middleware import StripContentTypeMiddleware
    mock = Mock()
    middleware = StripContentTypeMiddleware(mock)
    middleware({'REQUEST_METHOD': 'GET'}, None)

    assert 'CONTENT_TYPE' not in mock.call_args[0][0]


def test_middleware_strips_content_type_from_gets():
    from bigchaindb.web.strip_content_type_middleware import StripContentTypeMiddleware
    mock = Mock()
    middleware = StripContentTypeMiddleware(mock)
    middleware({'REQUEST_METHOD': 'GET',
                'CONTENT_TYPE': 'application/json'},
               None)

    assert 'CONTENT_TYPE' not in mock.call_args[0][0]


def test_middleware_does_notstrip_content_type_from_other_methods():
    from bigchaindb.web.strip_content_type_middleware import StripContentTypeMiddleware
    mock = Mock()
    middleware = StripContentTypeMiddleware(mock)
    middleware({'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/json'},
               None)

    assert 'CONTENT_TYPE' in mock.call_args[0][0]


def test_get_outputs_endpoint_with_content_type(client, user_pk):
    res = client.get(OUTPUTS_ENDPOINT + '?public_key={}'.format(user_pk),
                     headers=[('Content-Type', 'application/json')])
    assert res.status_code == 200
