import requests

import bigchaindb
from bigchaindb import util
from bigchaindb import config_utils
from bigchaindb import exceptions
from bigchaindb import crypto


class Client:
    """Client for BigchainDB.

    A Client is initialized with a keypair and is able to create, sign, and submit transactions to a Node
    in the Federation. At the moment, a Client instance is bounded to a specific ``host`` in the Federation.
    In the future, a Client might connect to >1 hosts.
    """

    def __init__(self, public_key=None, private_key=None, api_endpoint=None):
        """Initialize the Client instance

        There are three ways in which the Client instance can get its parameters.
        The order by which the parameters are chosen are:

            1. Setting them by passing them to the `__init__` method itself.
            2. Setting them as environment variables
            3. Reading them from the `config.json` file.

        Args:
            public_key (str): the base58 encoded public key for the ECDSA secp256k1 curve.
            private_key (str): the base58 encoded private key for the ECDSA secp256k1 curve.
            host (str): hostname where the rethinkdb is running.
            port (int): port in which rethinkb is running (usually 28015).
        """

        config_utils.autoconfigure()

        self.public_key = public_key or bigchaindb.config['keypair']['public']
        self.private_key = private_key or bigchaindb.config['keypair']['private']
        self.api_endpoint = api_endpoint or bigchaindb.config['api_endpoint']

        if not self.public_key or not self.private_key:
            raise exceptions.KeypairNotFoundException()

    def make_tx(self, new_owner, tx_input, operation='TRANSFER', payload=None):
        """Make a new transaction

        Refer to the documentation of ``bigchaindb.util.create_tx``
        """

        return util.create_tx(self.public_key, new_owner, tx_input, operation, payload)

    def sign_tx(self, tx):
        """Sign a transaction

        Refer to the documentation of ``bigchaindb.util.sign_tx``
        """

        return util.sign_tx(tx, self.private_key)

    def push_tx(self, tx):
        """Submit a transaction to the Federation.

        Args:
            tx (dict): the transaction to be pushed to the Federation.

        Return:
            The transaction pushed to the Federation.
        """

        res = requests.post(self.api_endpoint + '/transactions/', json=tx)
        return res.json()

    def create(self, payload=None):
        """Create a transaction.

        Args:
            payload (dict): the payload for the transaction.

        Return:
            The transaction pushed to the Federation.
        """

        tx = self.make_tx(self.public_key, None, operation='CREATE', payload=payload)
        signed_tx = self.sign_tx(tx)
        return self.push_tx(signed_tx)

    def transfer(self, new_owner, tx_input, payload=None):
        """Transfer a transaction.

        Args:
            new_owner (str): the public key of the new owner
            tx_input (str): the id of the transaction to use as input
            payload (dict, optional): the payload for the transaction.

        Return:
            The transaction pushed to the Federation.
        """

        tx = self.make_tx(new_owner, tx_input, payload=payload)
        signed_tx = self.sign_tx(tx)
        return self.push_tx(signed_tx)


def temp_client():
    """Create a new temporary client.

    Return:
        A client initialized with a keypair generated on the fly.
    """

    private_key, public_key = crypto.generate_key_pair()
    return Client(private_key=private_key, public_key=public_key, api_endpoint='http://localhost:5000/api/v1')

