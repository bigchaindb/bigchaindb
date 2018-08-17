# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

""" Script to build http examples for http server api docs """

import json
import os
import os.path

from bigchaindb.common.transaction import Transaction, Input, TransactionLink
from bigchaindb import lib
from bigchaindb.web import server


TPLS = {}


TPLS['index-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(index)s
"""

TPLS['api-index-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(api_index)s
"""

TPLS['get-tx-id-request'] = """\
GET /api/v1/transactions/%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-id-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(tx)s
"""


TPLS['get-tx-by-asset-request'] = """\
GET /api/v1/transactions?operation=TRANSFER&asset_id=%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-by-asset-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

[%(tx_transfer)s,
%(tx_transfer_last)s]
"""

TPLS['post-tx-request'] = """\
POST /api/v1/transactions?mode=async HTTP/1.1
Host: example.com
Content-Type: application/json

%(tx)s
"""


TPLS['post-tx-response'] = """\
HTTP/1.1 202 Accepted
Content-Type: application/json

%(tx)s
"""


TPLS['get-block-request'] = """\
GET /api/v1/blocks/%(blockid)s HTTP/1.1
Host: example.com

"""


TPLS['get-block-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(block)s
"""


TPLS['get-block-txid-request'] = """\
GET /api/v1/blocks?transaction_id=%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-block-txid-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(block_list)s
"""


def main():
    """ Main function """

    ctx = {}

    def pretty_json(data):
        return json.dumps(data, indent=2, sort_keys=True)

    client = server.create_app().test_client()

    host = 'example.com:9984'

    # HTTP Index
    res = client.get('/', environ_overrides={'HTTP_HOST': host})
    res_data = json.loads(res.data.decode())
    ctx['index'] = pretty_json(res_data)

    # API index
    res = client.get('/api/v1/', environ_overrides={'HTTP_HOST': host})
    ctx['api_index'] = pretty_json(json.loads(res.data.decode()))

    # tx create
    privkey = 'CfdqtD7sS7FgkMoGPXw55MVGGFwQLAoHYTcBhZDtF99Z'
    pubkey = '4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD'
    asset = {'msg': 'Hello BigchainDB!'}
    tx = Transaction.create([pubkey], [([pubkey], 1)], asset=asset, metadata={'sequence': 0})
    tx = tx.sign([privkey])
    ctx['tx'] = pretty_json(tx.to_dict())
    ctx['public_keys'] = tx.outputs[0].public_keys[0]
    ctx['txid'] = tx.id

    # tx transfer
    privkey_transfer = '3AeWpPdhEZzWLYfkfYHBfMFC2r1f8HEaGS9NtbbKssya'
    pubkey_transfer = '3yfQPHeWAa1MxTX9Zf9176QqcpcnWcanVZZbaHb8B3h9'

    cid = 0
    input_ = Input(fulfillment=tx.outputs[cid].fulfillment,
                   fulfills=TransactionLink(txid=tx.id, output=cid),
                   owners_before=tx.outputs[cid].public_keys)
    tx_transfer = Transaction.transfer([input_], [([pubkey_transfer], 1)], asset_id=tx.id, metadata={'sequence': 1})
    tx_transfer = tx_transfer.sign([privkey])
    ctx['tx_transfer'] = pretty_json(tx_transfer.to_dict())
    ctx['public_keys_transfer'] = tx_transfer.outputs[0].public_keys[0]
    ctx['tx_transfer_id'] = tx_transfer.id

    # privkey_transfer_last = 'sG3jWDtdTXUidBJK53ucSTrosktG616U3tQHBk81eQe'
    pubkey_transfer_last = '3Af3fhhjU6d9WecEM9Uw5hfom9kNEwE7YuDWdqAUssqm'

    cid = 0
    input_ = Input(fulfillment=tx_transfer.outputs[cid].fulfillment,
                   fulfills=TransactionLink(txid=tx_transfer.id, output=cid),
                   owners_before=tx_transfer.outputs[cid].public_keys)
    tx_transfer_last = Transaction.transfer([input_], [([pubkey_transfer_last], 1)],
                                            asset_id=tx.id, metadata={'sequence': 2})
    tx_transfer_last = tx_transfer_last.sign([privkey_transfer])
    ctx['tx_transfer_last'] = pretty_json(tx_transfer_last.to_dict())
    ctx['tx_transfer_last_id'] = tx_transfer_last.id
    ctx['public_keys_transfer_last'] = tx_transfer_last.outputs[0].public_keys[0]

    # block
    node_private = "5G2kE1zJAgTajkVSbPAQWo4c2izvtwqaNHYsaNpbbvxX"
    node_public = "DngBurxfeNVKZWCEcDnLj1eMPAS7focUZTE5FndFGuHT"
    signature = "53wxrEQDYk1dXzmvNSytbCfmNVnPqPkDQaTnAe8Jf43s6ssejPxezkCvUnGTnduNUmaLjhaan1iRLi3peu6s5DzA"

    app_hash = 'f6e0c49c6d94d6924351f25bb334cf2a99af4206339bf784e741d1a5ab599056'
    block = lib.Block(height=1, transactions=[tx.to_dict()], app_hash=app_hash)
    block_dict = block._asdict()
    block_dict.pop('app_hash')
    ctx['block'] = pretty_json(block_dict)
    ctx['blockid'] = block.height

    # block status
    block_list = [
        block.height
    ]
    ctx['block_list'] = pretty_json(block_list)


    base_path = os.path.join(os.path.dirname(__file__),
                             'source/http-samples')
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for name, tpl in TPLS.items():
        path = os.path.join(base_path, name + '.http')
        code = tpl % ctx
        with open(path, 'w') as handle:
            handle.write(code)


def setup(*_):
    """ Fool sphinx into think it's an extension muahaha """
    main()


if __name__ == '__main__':
    main()
