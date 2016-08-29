import random
import math
import collections
from copy import deepcopy

from itertools import compress
import rethinkdb as r
import rapidjson

import bigchaindb
from bigchaindb import config_utils, crypto, exceptions, util


class Bigchain(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    # return if a block has been voted invalid
    BLOCK_INVALID = 'invalid'
    # return if a block is valid, or tx is in valid block
    BLOCK_VALID = TX_VALID = 'valid'
    # return if block is undecided, or tx is in undecided block
    BLOCK_UNDECIDED = TX_UNDECIDED = 'undecided'
    # return if transaction is in backlog
    TX_IN_BACKLOG = 'backlog'

    def __init__(self, host=None, port=None, dbname=None,
                 public_key=None, private_key=None, keyring=[],
                 consensus_plugin=None):
        """Initialize the Bigchain instance

        A Bigchain instance has several configuration parameters (e.g. host).
        If a parameter value is passed as an argument to the Bigchain
        __init__ method, then that is the value it will have.
        Otherwise, the parameter value will come from an environment variable.
        If that environment variable isn't set, then the value
        will come from the local configuration file. And if that variable
        isn't in the local configuration file, then the parameter will have
        its default value (defined in bigchaindb.__init__).

        Args:
            host (str): hostname where RethinkDB is running.
            port (int): port in which RethinkDB is running (usually 28015).
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
        self.nodes_except_me = keyring or bigchaindb.config['keyring']
        self.consensus = config_utils.load_consensus_plugin(consensus_plugin)
        # change RethinkDB read mode to majority.  This ensures consistency in query results
        self.read_mode = 'majority'

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

        return self.consensus.sign_transaction(transaction, *args, bigchain=self, **kwargs)

    def validate_fulfillments(self, signed_transaction, *args, **kwargs):
        """Validate the fulfillment(s) of a transaction.

        Refer to the documentation of your consensus plugin.

        Returns:
            bool: True if the transaction's required fulfillments are present
                and correct, False otherwise.
        """

        return self.consensus.validate_fulfillments(
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

        if self.nodes_except_me:
            assignee = random.choice(self.nodes_except_me)
        else:
            # I am the only node
            assignee = self.me

        # We copy the transaction here to not add `assignee` to the transaction
        # dictionary passed to this method (as it would update by reference).
        signed_transaction = deepcopy(signed_transaction)
        # update the transaction
        signed_transaction.update({'assignee': assignee})

        # write to the backlog
        response = r.table('backlog').insert(signed_transaction, durability=durability).run(self.conn)
        return response

    def get_transaction(self, txid, include_status=False):
        """Retrieve a transaction with `txid` from bigchain.

        Queries the bigchain for a transaction, if it's in a valid or invalid
        block.

        Args:
            txid (str): transaction id of the transaction to query
            include_status (bool): also return the status of the transaction
                                   the return value is then a tuple: (tx, status)

        Returns:
            A dict with the transaction details if the transaction was found.
            Will add the transaction status to payload ('valid', 'undecided',
            or 'backlog'). If no transaction with that `txid` was found it
            returns `None`
        """

        response, tx_status = None, None

        validity = self.get_blocks_status_containing_tx(txid)

        if validity:
            # Disregard invalid blocks, and return if there are no valid or undecided blocks
            validity = {_id: status for _id, status in validity.items()
                                    if status != Bigchain.BLOCK_INVALID}
            if validity:

                tx_status = self.TX_UNDECIDED
                # If the transaction is in a valid or any undecided block, return it. Does not check
                # if transactions in undecided blocks are consistent, but selects the valid block before
                # undecided ones
                for target_block_id in validity:
                    if validity[target_block_id] == Bigchain.BLOCK_VALID:
                        tx_status = self.TX_VALID
                        break

                # Query the transaction in the target block and return
                response = r.table('bigchain', read_mode=self.read_mode).get(target_block_id)\
                    .get_field('block').get_field('transactions')\
                    .filter(lambda tx: tx['id'] == txid).run(self.conn)[0]

        else:
            # Otherwise, check the backlog
            response = r.table('backlog').get(txid).run(self.conn)
            if response:
                tx_status = self.TX_IN_BACKLOG

        if include_status:
            return response, tx_status
        else:
            return response

    def get_status(self, txid):
        """Retrieve the status of a transaction with `txid` from bigchain.

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            (string): transaction status ('valid', 'undecided',
            or 'backlog'). If no transaction with that `txid` was found it
            returns `None`
        """
        _, status = self.get_transaction(txid, include_status=True)
        return status

    def search_block_election_on_index(self, value, index):
        """Retrieve block election information given a secondary index and value

        Args:
            value: a value to search (e.g. transaction id string, payload hash string)
            index (str): name of a secondary index, e.g. 'transaction_id'

        Returns:
            A list of blocks with with only election information
        """
        # First, get information on all blocks which contain this transaction
        response = r.table('bigchain', read_mode=self.read_mode).get_all(value, index=index)\
            .pluck('votes', 'id', {'block': ['voters']}).run(self.conn)

        return list(response)

    def get_blocks_status_containing_tx(self, txid):
        """Retrieve block ids and statuses related to a transaction

        Transactions may occur in multiple blocks, but no more than one valid block.

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            A dict of blocks containing the transaction,
            e.g. {block_id_1: 'valid', block_id_2: 'invalid' ...}, or None
        """

        # First, get information on all blocks which contain this transaction
        blocks = self.search_block_election_on_index(txid, 'transaction_id')

        if blocks:
            # Determine the election status of each block
            validity = {block['id']: self.block_election_status(block) for block in blocks}

            # If there are multiple valid blocks with this transaction, something has gone wrong
            if list(validity.values()).count(Bigchain.BLOCK_VALID) > 1:
                block_ids = str([block for block in validity
                                       if validity[block] == Bigchain.BLOCK_VALID])
                raise Exception('Transaction {tx} is present in multiple valid blocks: {block_ids}'
                                .format(tx=txid, block_ids=block_ids))

            return validity

        else:
            return None

    def get_tx_by_payload_uuid(self, payload_uuid):
        """Retrieves transactions related to a digital asset.

        When creating a transaction one of the optional arguments is the `payload`. The payload is a generic
        dict that contains information about the digital asset.

        To make it easy to query the bigchain for that digital asset we create a UUID for the payload and 
        store it with the transaction. This makes it easy for developers to keep track of their digital 
        assets in bigchain.

        Args:
            payload_uuid (str): the UUID for this particular payload.

        Returns:
            A list of transactions containing that payload. If no transaction exists with that payload it
            returns an empty list `[]`
        """
        cursor = r.table('bigchain', read_mode=self.read_mode) \
            .get_all(payload_uuid, index='payload_uuid') \
            .concat_map(lambda block: block['block']['transactions']) \
            .filter(lambda transaction: transaction['transaction']['data']['uuid'] == payload_uuid) \
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
        response = r.table('bigchain', read_mode=self.read_mode)\
            .concat_map(lambda doc: doc['block']['transactions'])\
            .filter(lambda transaction: transaction['transaction']['fulfillments']
                    .contains(lambda fulfillment: fulfillment['input'] == tx_input))\
            .run(self.conn)

        transactions = list(response)

        # a transaction_id should have been spent at most one time
        if transactions:
            # determine if these valid transactions appear in more than one valid block
            num_valid_transactions = 0
            for transaction in transactions:
                # ignore invalid blocks
                if self.get_transaction(transaction['id']):
                    num_valid_transactions += 1
                if num_valid_transactions > 1:
                    raise exceptions.DoubleSpend('`{}` was spent more then once. There is a problem with the chain'.format(
                        tx_input['txid']))

            if num_valid_transactions:
                return transactions[0]
            else:
                # all queried transactions were invalid
                return None
        else:
            return None

    def get_owned_ids(self, owner):
        """Retrieve a list of `txids` that can we used has inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            list: list of `txids` currently owned by `owner`
        """

        # get all transactions in which owner is in the `owners_after` list
        response = r.table('bigchain', read_mode=self.read_mode) \
            .concat_map(lambda doc: doc['block']['transactions']) \
            .filter(lambda tx: tx['transaction']['conditions']
                    .contains(lambda c: c['owners_after']
                              .contains(owner))) \
            .run(self.conn)
        owned = []

        for tx in response:
            # disregard transactions from invalid blocks
            validity = self.get_blocks_status_containing_tx(tx['id'])
            if Bigchain.BLOCK_VALID not in validity.values():
                if Bigchain.BLOCK_UNDECIDED not in validity.values():
                    continue

            # a transaction can contain multiple outputs (conditions) so we need to iterate over all of them
            # to get a list of outputs available to spend
            for condition in tx['transaction']['conditions']:
                # for simple signature conditions there are no subfulfillments
                # check if the owner is in the condition `owners_after`
                if len(condition['owners_after']) == 1:
                    if condition['condition']['details']['public_key'] == owner:
                        tx_input = {'txid': tx['id'], 'cid': condition['cid']}
                else:
                    # for transactions with multiple `owners_after` there will be several subfulfillments nested
                    # in the condition. We need to iterate the subfulfillments to make sure there is a
                    # subfulfillment for `owner`
                    if util.condition_details_has_owner(condition['condition']['details'], owner):
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

        Similar to `validate_transaction` but never raises an exception.
        It returns `False` if the transaction is invalid.

        Args:
            transaction (dict): transaction to check.

        Returns:
            `transaction` if the transaction is valid, `False` otherwise
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

        # Prevent the creation of empty blocks
        if len(validated_transactions) == 0:
            raise exceptions.OperationError('Empty block creation is not allowed')

        # Create the new block
        block = {
            'timestamp': util.timestamp(),
            'transactions': validated_transactions,
            'node_pubkey': self.me,
            'voters': self.nodes_except_me + [self.me]
        }

        # Calculate the hash of the new block
        block_data = util.serialize(block)
        block_hash = crypto.hash_data(block_data)
        block_signature = crypto.SigningKey(self.me_private).sign(block_data)

        block = {
            'id': block_hash,
            'block': block,
            'signature': block_signature,
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
        # First, make sure this node hasn't already voted on this block
        if self.has_previous_vote(block):
            return block

        # Run the plugin block validation logic
        self.consensus.validate_block(self, block)

        # Finally: Tentative assumption that every blockchain will want to
        # validate all transactions in each block
        for transaction in block['block']['transactions']:
            if not self.is_valid_transaction(transaction):
                # this will raise the exception
                self.validate_transaction(transaction)

        return block

    def has_previous_vote(self, block):
        """Check for previous votes from this node

        Args:
            block (dict): block to check.

        Returns:
            bool: :const:`True` if this block already has a
            valid vote from this node, :const:`False` otherwise.

        Raises:
            ImproperVoteError: If there is already a vote,
                but the vote is invalid.

        """
        votes = list(r.table('votes', read_mode=self.read_mode)\
                     .get_all([block['id'], self.me], index='block_and_voter').run(self.conn))

        if len(votes) > 1:
            raise exceptions.MultipleVotesError('Block {block_id} has {n_votes} votes from public key {me}'
                                     .format(block_id=block['id'], n_votes=str(len(votes)), me=self.me))
        has_previous_vote = False
        if votes:
            if util.verify_vote_signature(block, votes[0]):
                has_previous_vote = True
            else:
                raise exceptions.ImproperVoteError('Block {block_id} already has an incorrectly signed vote '
                                        'from public key {me}'.format(block_id=block['id'], me=self.me))

        return has_previous_vote

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
        response = r.table('bigchain', read_mode=self.read_mode)\
            .get_all(transaction_id, index='transaction_id').run(self.conn)
        return True if len(response.items) > 0 else False

    def prepare_genesis_block(self):
        """Prepare a genesis block."""

        payload = {'message': 'Hello World from the BigchainDB'}
        transaction = self.create_transaction([self.me], [self.me], None, 'GENESIS', payload=payload)
        transaction_signed = self.sign_transaction(transaction, self.me_private)

        # create the block
        return self.create_block([transaction_signed])

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

        blocks_count = r.table('bigchain', read_mode=self.read_mode).count().run(self.conn)

        if blocks_count:
            raise exceptions.GenesisBlockAlreadyExistsError('Cannot create the Genesis block')

        block = self.prepare_genesis_block()
        self.write_block(block, durability='hard')

        return block

    def vote(self, block_id, previous_block_id, decision, invalid_reason=None):
        """Cast your vote on the block given the previous_block_hash and the decision (valid/invalid)
        return the block to the updated in the database.

        Args:
            block_id (str): The id of the block to vote.
            previous_block_id (str): The id of the previous block.
            decision (bool): Whether the block is valid or invalid.
            invalid_reason (Optional[str]): Reason the block is invalid
        """

        if block_id == previous_block_id:
            raise exceptions.CyclicBlockchainError()

        vote = {
            'voting_for_block': block_id,
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

    def write_vote(self, vote):
        """Write the vote to the database."""

        r.table('votes') \
            .insert(vote) \
            .run(self.conn)

    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        try:
            # get the latest value for the vote timestamp (over all votes)
            max_timestamp = r.table('votes', read_mode=self.read_mode) \
                .filter(r.row['node_pubkey'] == self.me) \
                .max(r.row['vote']['timestamp']) \
                .run(self.conn)['vote']['timestamp']

            last_voted = list(r.table('votes', read_mode=self.read_mode) \
                .filter(r.row['vote']['timestamp'] == max_timestamp) \
                .filter(r.row['node_pubkey'] == self.me) \
                .run(self.conn))

        except r.ReqlNonExistenceError:
            # return last vote if last vote exists else return Genesis block
            return list(r.table('bigchain', read_mode=self.read_mode)
                        .filter(util.is_genesis_block)
                        .run(self.conn))[0]

        # Now the fun starts. Since the resolution of timestamp is a second,
        # we might have more than one vote per timestamp. If this is the case
        # then we need to rebuild the chain for the blocks that have been retrieved
        # to get the last one.

        # Given a block_id, mapping returns the id of the block pointing at it.
        mapping = {v['vote']['previous_block']: v['vote']['voting_for_block']
                   for v in last_voted}

        # Since we follow the chain backwards, we can start from a random
        # point of the chain and "move up" from it.
        last_block_id = list(mapping.values())[0]

        # We must be sure to break the infinite loop. This happens when:
        # - the block we are currenty iterating is the one we are looking for.
        #   This will trigger a KeyError, breaking the loop
        # - we are visiting again a node we already explored, hence there is
        #   a loop. This might happen if a vote points both `previous_block`
        #   and `voting_for_block` to the same `block_id`
        explored = set()

        while True:
            try:
                if last_block_id in explored:
                    raise exceptions.CyclicBlockchainError()
                explored.add(last_block_id)
                last_block_id = mapping[last_block_id]
            except KeyError:
                break

        res = r.table('bigchain', read_mode=self.read_mode).get(last_block_id).run(self.conn)

        return res

    def get_unvoted_blocks(self):
        """Return all the blocks that has not been voted by this node."""

        unvoted = r.table('bigchain', read_mode=self.read_mode) \
            .filter(lambda block: r.table('votes', read_mode=self.read_mode)
                    .get_all([block['id'], self.me], index='block_and_voter')
                    .is_empty()) \
            .order_by(r.asc(r.row['block']['timestamp'])) \
            .run(self.conn)

        # FIXME: I (@vrde) don't like this solution. Filtering should be done at a
        #        database level. Solving issue #444 can help untangling the situation
        unvoted = filter(lambda block: not util.is_genesis_block(block), unvoted)

        return list(unvoted)

    def block_election_status(self, block):
        """Tally the votes on a block, and return the status: valid, invalid, or undecided."""

        votes = r.table('votes', read_mode=self.read_mode) \
            .between([block['id'], r.minval], [block['id'], r.maxval], index='block_and_voter') \
            .run(self.conn)

        votes = list(votes)

        n_voters = len(block['block']['voters'])

        voter_counts = collections.Counter([vote['node_pubkey'] for vote in votes])
        for node in voter_counts:
            if voter_counts[node] > 1:
                raise exceptions.MultipleVotesError('Block {block_id} has multiple votes ({n_votes}) from voting node {node_id}'
                                                    .format(block_id=block['id'], n_votes=str(voter_counts[node]), node_id=node))

        if len(votes) > n_voters:
            raise exceptions.MultipleVotesError('Block {block_id} has {n_votes} votes cast, but only {n_voters} voters'
                                                .format(block_id=block['id'], n_votes=str(len(votes)), n_voters=str(n_voters)))

        # vote_cast is the list of votes e.g. [True, True, False]
        vote_cast = [vote['vote']['is_block_valid'] for vote in votes]
        # prev_block are the ids of the nominal prev blocks e.g.
        # ['block1_id', 'block1_id', 'block2_id']
        prev_block = [vote['vote']['previous_block'] for vote in votes]
        # vote_validity checks whether a vote is valid
        # or invalid, e.g. [False, True, True]
        vote_validity = [self.consensus.verify_vote_signature(block, vote) for vote in votes]

        # element-wise product of stated vote and validity of vote
        # vote_cast = [True, True, False] and
        # vote_validity = [False, True, True] gives
        # [True, False]
        # Only the correctly signed votes are tallied.
        vote_list = list(compress(vote_cast, vote_validity))

        # Total the votes. Here, valid and invalid refer
        # to the vote cast, not whether the vote itself
        # is valid or invalid.
        n_valid_votes = sum(vote_list)
        n_invalid_votes = len(vote_cast) - n_valid_votes

        # The use of ceiling and floor is to account for the case of an
        # even number of voters where half the voters have voted 'invalid'
        # and half 'valid'. In this case, the block should be marked invalid
        # to avoid a tie. In the case of an odd number of voters this is not
        # relevant, since one side must be a majority.
        if n_invalid_votes >= math.ceil(n_voters / 2):
            return Bigchain.BLOCK_INVALID
        elif n_valid_votes > math.floor(n_voters / 2):
            # The block could be valid, but we still need to check if votes
            # agree on the previous block.
            #
            # First, only consider blocks with legitimate votes
            prev_block_list = list(compress(prev_block, vote_validity))
            # Next, only consider the blocks with 'yes' votes
            prev_block_valid_list = list(compress(prev_block_list, vote_list))
            counts = collections.Counter(prev_block_valid_list)
            # Make sure the majority vote agrees on previous node.
            # The majority vote must be the most common, by definition.
            # If it's not, there is no majority agreement on the previous
            # block.
            if counts.most_common()[0][1] > math.floor(n_voters / 2):
                return Bigchain.BLOCK_VALID
            else:
                return Bigchain.BLOCK_INVALID
        else:
            return Bigchain.BLOCK_UNDECIDED
