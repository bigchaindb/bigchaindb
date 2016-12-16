import pytest


UNSPENTS_ENDPOINT = '/api/v1/unspents/'


@pytest.mark.usefixtures('inputs')
def test_get_unspents_endpoint(b, client, user_pk):
    expected = [u.to_uri('..') for u in b.get_owned_ids(user_pk)]
    res = client.get(UNSPENTS_ENDPOINT + '?public_key={}'.format(user_pk))
    assert expected == res.json
    assert res.status_code == 200


@pytest.mark.usefixtures('inputs')
def test_get_unspents_endpoint_without_public_key(client):
    res = client.get(UNSPENTS_ENDPOINT)
    assert res.status_code == 400


@pytest.mark.usefixtures('inputs')
def test_get_unspents_endpoint_with_unused_public_key(client):
    expected = []
    res = client.get(UNSPENTS_ENDPOINT + '?public_key=abc')
    assert expected == res.json
    assert res.status_code == 200
