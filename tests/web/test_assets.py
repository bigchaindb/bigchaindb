from unittest.mock import patch

ASSETS_ENDPOINT = '/api/v1/assets/'


def test_get_assets_with_empty_text_search(client):
    res = client.get(ASSETS_ENDPOINT + '?text_search=')
    assert res.json == {'status': 400,
                        'message': 'text_search cannot be empty'}
    assert res.status_code == 400


def test_get_assets_with_missing_text_search(client):
    res = client.get(ASSETS_ENDPOINT)
    assert res.status_code == 400


def test_get_assets(client):
    with patch('bigchaindb.backend.query.text_search') as gof:
        gof.return_value = []
        res = client.get(ASSETS_ENDPOINT + '?text_search=abc')
    assert res.json == []
    assert res.status_code == 200
