""" Script to build http examples for http server api docs """

import json
import os
import os.path

from bigchaindb.common.transaction import Transaction


TPLS = {}

TPLS['post-tx-request'] = """\
POST /transactions/ HTTP/1.1
Host: example.com
Content-Type: application/json

%(tx)s
"""


TPLS['post-tx-response'] = """\
HTTP/1.1 201 Created
Content-Type: application/json

%(tx)s
"""


TPLS['get-tx-status-request'] = """\
GET /transactions/%(txid)s/status HTTP/1.1
Host: example.com

"""


TPLS['get-tx-status-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "valid"
}
"""


TPLS['get-tx-request'] = """\
GET /transactions/%(txid)s HTTP/1.1
Host: example.com

"""


TPLS['get-tx-response'] = """\
HTTP/1.1 200 OK
Content-Type: application/json

%(tx)s
"""


def main():
    """ Main function """
    privkey = 'CfdqtD7sS7FgkMoGPXw55MVGGFwQLAoHYTcBhZDtF99Z'
    pubkey = '4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD'
    tx = Transaction.create([pubkey], [([pubkey], 1)])
    tx = tx.sign([privkey])
    tx_json = json.dumps(tx.to_dict(), indent=2, sort_keys=True)

    base_path = os.path.join(os.path.dirname(__file__),
                             'source/drivers-clients/samples')

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for name, tpl in TPLS.items():
        path = os.path.join(base_path, name + '.http')
        code = tpl % {'tx': tx_json, 'txid': tx.id}
        with open(path, 'w') as handle:
            handle.write(code)


def setup(*_):
    """ Fool sphinx into think it's an extension muahaha """
    main()


if __name__ == '__main__':
    main()
