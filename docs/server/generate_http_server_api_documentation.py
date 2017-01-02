""" Script to build http examples for http server api docs """

import json
import os
import os.path

from bigchaindb.common.transaction import Transaction, Input, TransactionLink
from bigchaindb.models import Block


TPLS = {}


TPLS['get-tx-id-request'] = """\
GET /transactions/%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-id-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json
X-BigchainDB-Timestamp: 1482766245

%(tx)s
"""


TPLS['get-tx-unfulfilled-request'] = """\
GET /transactions?fulfilled=false&public_keys=%(public_keys_transfer_last)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-unfulfilled-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

[%(tx_transfer_last)s]
"""


TPLS['get-tx-by-asset-request'] = """\
GET /transactions?operation=transfer&asset_id=%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-by-asset-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

[%(tx_transfer)s,
%(tx_transfer_last)s]
"""


TPLS['post-tx-request'] = """\
POST /transactions/ HTTP/1.1
Host: example.com
Content-Type: application/json

%(tx)s
"""


TPLS['post-tx-response'] = """\
HTTP/1.1 202 Accepted
Content-Type: application/json
Location: ../statuses/%(txid)s
"""


TPLS['get-statuses-tx-request'] = """\
GET /statuses/%(txid)s HTTP/1.1
Host: example.com

"""

TPLS['get-statuses-tx-invalid-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "invalid"
}
"""


TPLS['get-statuses-tx-valid-response'] = """\
HTTP/1.1 303 See Other
Content-Type: application/json
Location: ../transactions/%(txid)s

{
  "status": "valid"
}
"""


TPLS['get-block-request'] = """\
GET /blocks/%(blockid)s HTTP/1.1
Host: example.com

"""

TPLS['get-block-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(block)s
"""

TPLS['get-block-txid-request'] = """\
GET /blocks?tx_id=%(txid)s HTTP/1.1
Host: example.com

"""

TPLS['get-block-txid-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

[%(block)s]
"""


def main():
    """ Main function """
    privkey = 'CfdqtD7sS7FgkMoGPXw55MVGGFwQLAoHYTcBhZDtF99Z'
    pubkey = '4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD'
    asset = {'msg': 'Hello BigchainDB!'}
    tx = Transaction.create([pubkey], [([pubkey], 1)], asset=asset)
    tx = tx.sign([privkey])
    tx_json = json.dumps(tx.to_dict(), indent=2, sort_keys=True)

    privkey_transfer = '3AeWpPdhEZzWLYfkfYHBfMFC2r1f8HEaGS9NtbbKssya'
    pubkey_transfer = '3yfQPHeWAa1MxTX9Zf9176QqcpcnWcanVZZbaHb8B3h9'

    cid = 0
    input_ = Input(fulfillment=tx.outputs[cid].fulfillment,
                   fulfills=TransactionLink(txid=tx.id, output=cid),
                   owners_before=tx.outputs[cid].public_keys)
    tx_transfer = Transaction.transfer([input_], [([pubkey_transfer], 1)], asset_id=tx.id)
    tx_transfer = tx_transfer.sign([privkey])
    tx_transfer_json = json.dumps(tx_transfer.to_dict(), indent=2, sort_keys=True)

    privkey_transfer_last = 'sG3jWDtdTXUidBJK53ucSTrosktG616U3tQHBk81eQe'
    pubkey_transfer_last = '3Af3fhhjU6d9WecEM9Uw5hfom9kNEwE7YuDWdqAUssqm'

    cid = 0
    input_ = Input(fulfillment=tx_transfer.outputs[cid].fulfillment,
                   fulfills=TransactionLink(txid=tx_transfer.id, output=cid),
                   owners_before=tx_transfer.outputs[cid].public_keys)
    tx_transfer_last = Transaction.transfer([input_], [([pubkey_transfer_last], 1)], asset_id=tx.id)
    tx_transfer_last = tx_transfer_last.sign([privkey_transfer])
    tx_transfer_last_json = json.dumps(tx_transfer_last.to_dict(), indent=2, sort_keys=True)

    node = "ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt"
    signature = "53wxrEQDYk1dXzmvNSytbCfmNVnPqPkDQaTnAe8Jf43s6ssejPxezkCvUnGTnduNUmaLjhaan1iRLi3peu6s5DzA"
    block = Block(transactions=[tx], node_pubkey=node, voters=[node], signature=signature)
    block_json = json.dumps(block.to_dict(), indent=2, sort_keys=True)

    base_path = os.path.join(os.path.dirname(__file__),
                             'source/drivers-clients/samples')

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for name, tpl in TPLS.items():
        path = os.path.join(base_path, name + '.http')
        code = tpl % {'tx': tx_json,
                      'txid': tx.id,
                      'tx_transfer': tx_transfer_json,
                      'tx_transfer_id': tx_transfer.id,
                      'tx_transfer_last': tx_transfer_last_json,
                      'tx_transfer_last_id': tx_transfer_last.id,
                      'public_keys': tx.outputs[0].public_keys[0],
                      'public_keys_transfer': tx_transfer.outputs[0].public_keys[0],
                      'public_keys_transfer_last': tx_transfer_last.outputs[0].public_keys[0],
                      'block': block_json,
                      'blockid': block.id}
        with open(path, 'w') as handle:
            handle.write(code)


def setup(*_):
    """ Fool sphinx into think it's an extension muahaha """
    main()


if __name__ == '__main__':
    main()


