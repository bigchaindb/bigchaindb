from pytest import raises


def test_asset_default_values():
    from bigchaindb.common.transaction import Asset

    asset = Asset()
    assert asset.data is None
    assert asset.data_id


def test_asset_creation_with_data(data):
    from bigchaindb.common.transaction import Asset

    asset = Asset(data)
    assert asset.data == data


def test_asset_invalid_asset_initialization():
    from bigchaindb.common.transaction import Asset

    # check types
    with raises(TypeError):
        Asset(data='some wrong type')


def test_invalid_asset_comparison(data, data_id):
    from bigchaindb.common.transaction import Asset

    assert Asset(data, data_id) != 'invalid comparison'


def test_asset_serialization(data, data_id):
    from bigchaindb.common.transaction import Asset

    expected = {
        'id': data_id,
        'data': data,
    }
    asset = Asset(data, data_id)
    assert asset.to_dict() == expected


def test_asset_deserialization(data, data_id):
    from bigchaindb.common.transaction import Asset

    asset_dict = {
        'id': data_id,
        'data': data,
    }
    asset = Asset.from_dict(asset_dict)
    expected = Asset(data, data_id)
    assert asset == expected


def test_validate_asset():
    from bigchaindb.common.transaction import Asset

    # test amount errors
    asset = Asset()
    with raises(TypeError):
        asset.validate_asset(amount='a')
