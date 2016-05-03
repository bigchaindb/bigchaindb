import random
import math
import operator

import rethinkdb as r
import rapidjson

import bigchaindb
from bigchaindb import util
from bigchaindb import config_utils
from bigchaindb import exceptions
from bigchaindb import crypto


class GenesisBlockAlreadyExistsError(Exception):
    pass


class Bigchain(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    def __init__(self, host=None, port=None, dbname=None,
                 public_key=None, private_key=None, keyring=[],
                 consensus_plugin=None):
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
            public_key (str): the base58 encoded public key for the ED25519 curve.
            private_key (str): the base58 encoded private key for the ED25519 curve.
            keyring (list[str]): list of base58 encoded public keys of the federation nodes.
        """

        config_utils.autoconfigure()
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = dbname or bigchaindb.config['database']['name']
        self.me = public_key or bigchaindb.config['keypair']['public']
        self.me_private = private_key or bigchaindb.config['keypair']['private']
        self.federation_nodes = keyring or bigchaindb.config['keyring']
        self.consensus = config_utils.load_consensus_plugin(consensus_plugin)

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

    def create_transaction(self, *args, **kwargs):
        """Create a new transaction

        Refer to the documentation of your consensus plugin.

        Returns:
            dict: newly constructed transaction.
        """

        return self.consensus.create_transaction(*args, **kwargs)

    def sign_transaction(self, transaction, *args, **kwargs):
        """Sign a transaction

        Refer to the documentation of your consensus plugin.

        Returns:
            dict: transaction with any signatures applied.
        """

        return self.consensus.sign_transaction(transaction, *args, **kwargs)

    def verify_signature(self, signed_transaction, *args, **kwargs):
        """Verify the signature(s) of a transaction.

        Refer to the documentation of your consensus plugin.

        Returns:
            bool: True if the transaction's required signature data is present
                and correct, False otherwise.
        """

        return self.consensus.verify_signature(
            signed_transaction, *args, **kwargs)

    def write_transaction(self, signed_transaction, durability='soft'):
        """Write the transaction to bigchain.

        When first writing a transaction to the bigchain the transaction will be kept in a backlog until
        it has been validated by the nodes of the federation.

        Args:
            signed_transaction (dict): transaction with the `signature` included.

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
            returns an empty list `[]`
        """

        cursor = r.table('bigchain') \
            .get_all(payload_hash, index='payload_hash') \
            .run(self.conn)

        transactions = list(cursor)
        return transactions

    def get_spent(self, tx_input):
        """Check if a `txid` was already used as an input.

        A transaction can be used as an input for another transaction. Bigchain needs to make sure that a
        given `txid` is only used once.

        Args:
            tx_input (dict): Input of a transaction in the form `{'txid': 'transaction id', 'cid': 'condition id'}`

        Returns:
            The transaction that used the `txid` as an input if it exists else it returns `None`
        """
        # checks if an input was already spent
        # checks if the bigchain has any transaction with input {'txid': ..., 'cid': ...}
        response = r.table('bigchain').concat_map(lambda doc: doc['block']['transactions'])\
            .filter(lambda transaction: transaction['transaction']['fulfillments']
                    .contains(lambda fulfillment: fulfillment['input'] == tx_input))\
            .run(self.conn)

        # a transaction_id should have been spent at most one time
        transactions = list(response)
        if transactions:
            if len(transactions) != 1:
                raise exceptions.DoubleSpend('`{}` was spent more then once. There is a problem with the chain'.format(
                    tx_input['txid']))
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

        # get all transactions in which owner is in the `new_owners` list
        response = r.table('bigchain') \
            .concat_map(lambda doc: doc['block']['transactions']) \
            .filter(lambda tx: tx['transaction']['conditions']
                    .contains(lambda c: c['new_owners']
                              .contains(owner))) \
            .run(self.conn)
        owned = []

        for tx in response:
            # a transaction can contain multiple outputs (conditions) so we need to iterate over all of them
            # to get a list of outputs available to spend
            for condition in tx['transaction']['conditions']:
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `new_owners`
                if len(condition['new_owners']) == 1:
                    if condition['condition']['details']['public_key'] == owner:
                        tx_input = {'txid': tx['id'], 'cid': condition['cid']}
                else:
                    # for transactions with multiple `new_owners` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    for subfulfillment in condition['condition']['details']['subfulfillments']:
                        if subfulfillment['public_key'] == owner:
                            tx_input = {'txid': tx['id'], 'cid': condition['cid']}
                # check if input was already spent
                if not self.get_spent(tx_input):
                    owned.append(tx_input)

        return owned

    def validate_transaction(self, transaction):
        """Validate a transaction.

        Args:
            transaction (dict): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.
        """

        return self.consensus.validate_transaction(self, transaction)

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
        block_hash = crypto.hash_data(block_data)
        block_signature = crypto.SigningKey(self.me_private).sign(block_data)

        block = {
            'id': block_hash,
            'block': block,
            'signature': block_signature,
            'votes': []
        }

        return block

    # TODO: check that the votings structure is correctly constructed
    def validate_block(self, block):
        """Validate a block.

        Args:
            block (dict): block to validate.

        Returns:
            The block if the block is valid else it raises and exception
            describing the reason why the block is invalid.
        """

        # First: Run the plugin block validation logic
        self.consensus.validate_block(self, block)

        # Finally: Tentative assumption that every blockchain will want to
        # validate all transactions in each block
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

    # TODO: Unless we prescribe the signature of create_transaction, this will
    #       also need to be moved into the plugin API.
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
        transaction = self.create_transaction([self.me], [self.me], None, 'GENESIS', payload=payload)
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
        signature = crypto.SigningKey(self.me_private).sign(vote_data)

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

        r.table('bigchain') \
            .get(vote['vote']['voting_for_block']) \
            .update(update) \
            .run(self.conn)

    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        # query bigchain for all blocks this node is a voter but didn't voted on
        last_voted = r.table('bigchain') \
            .filter(r.row['block']['voters'].contains(self.me)) \
            .filter(lambda doc: doc['votes'].contains(lambda vote: vote['node_pubkey'] == self.me)) \
            .order_by(r.desc('block_number')) \
            .limit(1) \
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

        unvoted = r.table('bigchain') \
            .filter(lambda doc: doc['votes'].contains(lambda vote: vote['node_pubkey'] == self.me).not_()) \
            .order_by(r.asc((r.row['block']['timestamp']))) \
            .run(self.conn)

        if unvoted and unvoted[0].get('block_number') == 0:
            unvoted.pop(0)

        return unvoted

    def block_election_status(self, block):
        """
        Tallies the votes on a block, and returns the status: valid, invalid, or undecided
        """
        n_voters = len(block['block']['voters'])

        vote_cast = [vote['vote']['is_block_valid'] for vote in block['block']['votes']]
        vote_validity = [self.consensus.verify_vote_signature(block, vote) for vote in block['block']['votes']]

        # element-wise product of stated vote and validity of vote
        vote_list = list(map(operator.mul, vote_cast, vote_validity))

        # validate votes here
        n_valid_votes = sum(vote_list)
        n_invalid_votes = len(vote_list) - n_valid_votes

        if n_invalid_votes >= math.ceil(n_voters / 2):
            return 'invalid'
        elif n_valid_votes > math.floor(n_voters / 2):
            return 'valid'
        else:
            return 'undecided'
