import pytest


@pytest.mark.usefixtures('inputs')
def test_tx_endpoint(b, client, user_public_key):
    input_tx = b.get_owned_ids(user_public_key).pop()
    tx = b.get_transaction(input_tx)

    res = client.get('/tx/{}'.format(input_tx))
    assert tx == res.json
