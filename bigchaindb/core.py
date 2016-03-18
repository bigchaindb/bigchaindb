import random
import rapidjson

import rethinkdb as r

import bigchaindb
from bigchaindb import config_utils
from bigchaindb import exceptions
from bigchaindb import util
from bigchaindb.crypto import asymmetric
from bigchaindb.monitor import Monitor

monitor = Monitor()


class GenesisBlockAlreadyExistsError(Exception):
    pass


class Bigchain(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    def __init__(self, host=None, port=None, dbname=None,
                 public_key=None, private_key=None, keyring=[]):
        """Initialize the Bigchain instance

        There are three ways in which the Bigchain instance can get its parameters.
        The order by which the parameters are chosen are:

            1. Setting them by passing them to the `__init__` method itself.
            2. Setting them as environment variables
            3. Reading them from the `config.json` file.

        Args:
            host (str): hostname where the rethinkdb is running.
            port (int): port in which rethinkb is running (usually 28015).
            dbname (str): the name of the database to connect to (usually bigchain).
            public_key (str): the base58 encoded public key for the ECDSA secp256k1 curve.
            private_key (str): the base58 encoded private key for the ECDSA secp256k1 curve.
            keyring (list[str]): list of base58 encoded public keys of the federation nodes.
        """

        config_utils.autoconfigure()
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = dbname or bigchaindb.config['database']['name']
        self.me = public_key or bigchaindb.config['keypair']['public']
        self.me_private = private_key or bigchaindb.config['keypair']['private']
        self.federation_nodes = keyring or bigchaindb.config['keyring']

        if not self.me or not self.me_private:
            raise exceptions.KeypairNotFoundException()

        self._conn = None

    @property
    def conn(self):
        if not self._conn:
            self._conn = self.reconnect()
        return self._conn

    def reconnect(self):
        return r.connect(host=self.host, port=self.port, db=self.dbname)

    @monitor.timer('create_transaction', rate=bigchaindb.config['statsd']['rate'])
    def create_transaction(self, current_owner, new_owner, tx_input, operation, payload=None):
        """Create a new transaction

        Refer to the documentation of ``bigchaindb.util.create_tx``
        """

        return util.create_tx(current_owner, new_owner, tx_input, operation, payload)

    def sign_transaction(self, transaction, private_key):
        """Sign a transaction

        Refer to the documentation of ``bigchaindb.util.sign_tx``
        """

        return util.sign_tx(transaction, private_key)

    def verify_signature(self, signed_transaction):
        """Verify the signature of a transaction.

        Refer to the documentation of ``bigchaindb.crypto.verify_signature``
        """

        data = signed_transaction.copy()

        # if assignee field in the transaction, remove it
        if 'assignee' in data:
            data.pop('assignee')

        signature = data.pop('signature')
        public_key_base58 = signed_transaction['transaction']['current_owner']
        public_key = asymmetric.PublicKey(public_key_base58)
        return public_key.verify(util.serialize(data), signature)

    @monitor.timer('write_transaction', rate=bigchaindb.config['statsd']['rate'])
    def write_transaction(self, signed_transaction, durability='soft'):
        """Write the transaction to bigchain.

        When first writing a transaction to the bigchain the transaction will be kept in a backlog until
        it has been validated by the nodes of the federation.

        Args:
            singed_transaction (dict): transaction with the `signature` included.

        Returns:
            dict: database response
        """

        # we will assign this transaction to `one` node. This way we make sure that there are no duplicate
        # transactions on the bigchain

        if self.federation_nodes:
            assignee = random.choice(self.federation_nodes)
        else:
            # I am the only node
            assignee = self.me

        # update the transaction
        signed_transaction.update({'assignee': assignee})

        # write to the backlog
        response = r.table('backlog').insert(signed_transaction, durability=durability).run(self.conn)
        return response

    # TODO: the same `txid` can be in two different blocks
    def get_transaction(self, txid):
        """Retrieve a transaction with `txid` from bigchain.

        Queries the bigchain for a transaction that was already included in a block.

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            A dict with the transaction details if the transaction was found.

            If no transaction with that `txid` was found it returns `None`
        """

        response = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
            .filter(lambda transaction: transaction['id'] == txid).run(self.conn)

        # transaction ids should be unique
        transactions = list(response)
        if transactions:
            if len(transactions) != 1:
                raise Exception('Transaction ids should be unique. There is a problem with the chain')
            else:
                return transactions[0]
        else:
            return None

    def get_tx_by_payload_hash(self, payload_hash):
        """Retrieves transactions related to a digital asset.

        When creating a transaction one of the optional arguments is the `payload`. The payload is a generic
        dict that contains information about the digital asset.

        To make it easy to query the bigchain for that digital asset we create a sha3-256 hash of the
        serialized payload and store it with the transaction. This makes it easy for developers to keep track
        of their digital assets in bigchain.

        Args:
            payload_hash (str): sha3-256 hash of the serialized payload.

        Returns:
            A list of transactions containing that payload. If no transaction exists with that payload it
            returns `None`
        """

        cursor = r.table('bigchain')\
            .get_all(payload_hash, index='payload_hash')\
            .run(self.conn)

        transactions = list(cursor)
        return transactions

    def get_spent(self, txid):
        """Check if a `txid` was already used as an input.

        A transaction can be used as an input for another transaction. Bigchain needs to make sure that a
        given `txid` is only used once.

        Args:
            txid (str): transaction id.

        Returns:
            The transaction that used the `txid` as an input if it exists else it returns `None`
        """
        # checks if an input was already spent
        # checks if the bigchain has any transaction with input `transaction_id`
        response = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
            .filter(lambda transaction: transaction['transaction']['input'] == txid).run(self.conn)

        # a transaction_id should have been spent at most one time
        transactions = list(response)
        if transactions:
            if len(transactions) != 1:
                raise Exception('`{}` was spent more then once. There is a problem with the chain'.format(
                    txid))
            else:
                return transactions[0]
        else:
            return None

    def get_owned_ids(self, owner):
        """Retrieve a list of `txids` that can we used has inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            list: list of `txids` currently owned by `owner`
        """

        response = r.table('bigchain')\
                    .concat_map(lambda doc: doc['block']['transactions'])\
                    .filter({'transaction': {'new_owner': owner}})\
                    .pluck('id')['id']\
                    .run(self.conn)
        owned = []

        # remove all inputs already spent
        for tx_input in list(response):
            if not self.get_spent(tx_input):
                owned.append(tx_input)

        return owned

    @monitor.timer('validate_transaction', rate=bigchaindb.config['statsd']['rate'])
    def validate_transaction(self, transaction):
        """Validate a transaction.

        Args:
            transaction (dict): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises and exception
            describing the reason why the transaction is invalid.

        Raises:
            OperationError: if the transaction operation is not supported
            TransactionDoesNotExist: if the input of the transaction is not found
            TransactionOwnerError: if the new transaction is using an input it doesn't own
            DoubleSpend: if the transaction is a double spend
            InvalidHash: if the hash of the transaction is wrong
            InvalidSignature: if the signature of the transaction is wrong
        """

        # If the operation is CREATE the transaction should have no inputs and should be signed by a
        # federation node
        if transaction['transaction']['operation'] == 'CREATE':
            if transaction['transaction']['input']:
                raise ValueError('A CREATE operation has no inputs')
            if transaction['transaction']['current_owner'] not in self.federation_nodes + [self.me]:
                raise exceptions.OperationError('Only federation nodes can use the operation `CREATE`')

        else:
            # check if the input exists, is owned by the current_owner
            if not transaction['transaction']['input']:
                raise ValueError('Only `CREATE` transactions can have null inputs')

            tx_input = self.get_transaction(transaction['transaction']['input'])
            if not tx_input:
                raise exceptions.TransactionDoesNotExist('input `{}` does not exist in the bigchain'.format(
                    transaction['transaction']['input']))

            if tx_input['transaction']['new_owner'] != transaction['transaction']['current_owner']:
                raise exceptions.TransactionOwnerError('current_owner `{}` does not own the input `{}`'.format(
                    transaction['transaction']['current_owner'], transaction['transaction']['input']))

            # check if the input was already spent by a transaction other then this one.
            spent = self.get_spent(tx_input['id'])
            if spent:
                if spent['id'] != transaction['id']:
                    raise exceptions.DoubleSpend('input `{}` was already spent'.format(
                        transaction['transaction']['input']))

        util.check_hash_and_signature(transaction)
        return transaction

    def is_valid_transaction(self, transaction):
        """Check whether a transacion is valid or invalid.

        Similar to `validate_transaction` but does not raise an exception if the transaction is valid.

        Args:
            transaction (dict): transaction to check.

        Returns:
            bool: `True` if the transaction is valid, `False` otherwise
        """

        try:
            self.validate_transaction(transaction)
            return transaction
        except (ValueError, exceptions.OperationError, exceptions.TransactionDoesNotExist,
                exceptions.TransactionOwnerError, exceptions.DoubleSpend,
                exceptions.InvalidHash, exceptions.InvalidSignature):
            return False

    def create_block(self, validated_transactions):
        """Creates a block given a list of `validated_transactions`.

        Note that this method does not validate the transactions. Transactions should be validated before
        calling create_block.

        Args:
            validated_transactions (list): list of validated transactions.

        Returns:
            dict: created block.
        """

        # Create the new block
        block = {
            'timestamp': util.timestamp(),
            'transactions': validated_transactions,
            'node_pubkey': self.me,
            'voters': self.federation_nodes + [self.me]
        }

        # Calculate the hash of the new block
        block_data = util.serialize(block)
        block_hash = asymmetric.hash_data(block_data)
        block_signature = asymmetric.PrivateKey(self.me_private).sign(block_data)

        block = {
            'id': block_hash,
            'block': block,
            'signature': block_signature,
            'votes': []
        }

        return block

    @monitor.timer('validate_block')
    # TODO: check that the votings structure is correctly constructed
    def validate_block(self, block):
        """Validate a block.

        Args:
            block (dict): block to validate.

        Returns:
            The block if the block is valid else it raises and exception
            describing the reason why the block is invalid.
        """

        # 1. Check if current hash is correct
        calculated_hash = asymmetric.hash_data(util.serialize(block['block']))
        if calculated_hash != block['id']:
            raise exceptions.InvalidHash()

        # 2. Validate all transactions in the block
        for transaction in block['block']['transactions']:
            if not self.is_valid_transaction(transaction):
                # this will raise the exception
                self.validate_transaction(transaction)

        return block

    def is_valid_block(self, block):
        """Check whether a block is valid or invalid.

        Similar to `validate_block` but does not raise an exception if the block is invalid.

        Args:
            block (dict): block to check.

        Returns:
            bool: `True` if the block is valid, `False` otherwise.
        """

        try:
            self.validate_block(block)
            return True
        except Exception:
            return False

    @monitor.timer('write_block')
    def write_block(self, block, durability='soft'):
        """Write a block to bigchain.

        Args:
            block (dict): block to write to bigchain.
        """

        block_serialized = rapidjson.dumps(block)
        r.table('bigchain').insert(r.json(block_serialized), durability=durability).run(self.conn)

    # TODO: Decide if we need this method
    def transaction_exists(self, transaction_id):
        response = r.table('bigchain').get_all(transaction_id, index='transaction_id').run(self.conn)
        return True if len(response.items) > 0 else False

    def create_genesis_block(self):
        """Create the genesis block

        Block created when bigchain is first initialized. This method is not atomic, there might be concurrency
        problems if multiple instances try to write the genesis block when the BigchainDB Federation is started,
        but it's a highly unlikely scenario.
        """

        # 1. create one transaction
        # 2. create the block with one transaction
        # 3. write the block to the bigchain

        blocks_count = r.table('bigchain').count().run(self.conn)

        if blocks_count:
            raise GenesisBlockAlreadyExistsError('Cannot create the Genesis block')

        payload = {'message': 'Hello World from the BigchainDB'}
        transaction = self.create_transaction(self.me, self.me, None, 'GENESIS', payload=payload)
        transaction_signed = self.sign_transaction(transaction, self.me_private)

        # create the block
        block = self.create_block([transaction_signed])
        # add block number before writing
        block['block_number'] = 0
        self.write_block(block, durability='hard')

        return block

    def vote(self, block, previous_block_id, decision, invalid_reason=None):
        """Cast your vote on the block given the previous_block_hash and the decision (valid/invalid)
        return the block to the updated in the database.

        Args:
            block (dict): Block to vote.
            previous_block_id (str): The id of the previous block.
            decision (bool): Whether the block is valid or invalid.
            invalid_reason (Optional[str]): Reason the block is invalid
        """

        vote = {
            'voting_for_block': block['id'],
            'previous_block': previous_block_id,
            'is_block_valid': decision,
            'invalid_reason': invalid_reason,
            'timestamp': util.timestamp()
        }

        vote_data = util.serialize(vote)
        signature = asymmetric.PrivateKey(self.me_private).sign(vote_data)

        vote_signed = {
            'node_pubkey': self.me,
            'signature': signature,
            'vote': vote
        }

        return vote_signed

    def write_vote(self, block, vote, block_number):
        """Write the vote to the database."""

        update = {'votes': r.row['votes'].append(vote)}

        # We need to *not* override the existing block_number, if any
        # FIXME: MIGHT HAVE RACE CONDITIONS WITH THE OTHER NODES IN THE FEDERATION
        if 'block_number' not in block:
            update['block_number'] = block_number

        r.table('bigchain')\
         .get(vote['vote']['voting_for_block'])\
         .update(update)\
         .run(self.conn)

    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        # query bigchain for all blocks this node is a voter but didn't voted on
        last_voted = r.table('bigchain')\
            .filter(r.row['block']['voters'].contains(self.me))\
            .filter(lambda doc: doc['votes'].contains(lambda vote: vote['node_pubkey'] == self.me))\
            .order_by(r.desc('block_number'))\
            .limit(1)\
            .run(self.conn)

        # return last vote if last vote exists else return Genesis block
        last_voted = list(last_voted)
        if not last_voted:
            return list(r.table('bigchain')
                         .filter(r.row['block_number'] == 0)
                         .run(self.conn))[0]

        return last_voted[0]

    def get_unvoted_blocks(self):
        """Return all the blocks that has not been voted by this node."""

        unvoted = r.table('bigchain')\
            .filter(lambda doc: doc['votes'].contains(lambda vote: vote['node_pubkey'] == self.me).not_())\
            .order_by(r.asc((r.row['block']['timestamp'])))\
            .run(self.conn)

        if unvoted and unvoted[0].get('block_number') == 0:
            unvoted.pop(0)

        return unvoted

