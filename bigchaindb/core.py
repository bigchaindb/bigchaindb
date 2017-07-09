import random
import statsd
from time import time

from bigchaindb import exceptions as core_exceptions
from bigchaindb.common import crypto, exceptions
from bigchaindb.common.utils import gen_timestamp, serialize

import bigchaindb

from bigchaindb import backend, config_utils, fastquery
from bigchaindb.consensus import BaseConsensusRules
from bigchaindb.models import Block, Transaction


class Bigchain(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    BLOCK_INVALID = 'invalid'
    """return if a block has been voted invalid"""

    BLOCK_VALID = TX_VALID = 'valid'
    """return if a block is valid, or tx is in valid block"""

    BLOCK_UNDECIDED = TX_UNDECIDED = 'undecided'
    """return if block is undecided, or tx is in undecided block"""

    TX_IN_BACKLOG = 'backlog'
    """return if transaction is in backlog"""

    def __init__(self, public_key=None, private_key=None, keyring=[], connection=None, backlog_reassign_delay=None):
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
            public_key (str): the base58 encoded public key for the ED25519 curve.
            private_key (str): the base58 encoded private key for the ED25519 curve.
            keyring (list[str]): list of base58 encoded public keys of the federation nodes.
            connection (:class:`~bigchaindb.backend.connection.Connection`):
                A connection to the database.
        """

        config_utils.autoconfigure()

        self.me = public_key or bigchaindb.config['keypair']['public']
        self.me_private = private_key or bigchaindb.config['keypair']['private']
        self.nodes_except_me = keyring or bigchaindb.config['keyring']

        if backlog_reassign_delay is None:
            backlog_reassign_delay = bigchaindb.config['backlog_reassign_delay']
        self.backlog_reassign_delay = backlog_reassign_delay

        consensusPlugin = bigchaindb.config.get('consensus_plugin')

        if consensusPlugin:
            self.consensus = config_utils.load_consensus_plugin(consensusPlugin)
        else:
            self.consensus = BaseConsensusRules

        self.connection = connection if connection else backend.connect(**bigchaindb.config['database'])
        if not self.me or not self.me_private:
            raise exceptions.KeypairNotFoundException()

        self.statsd = statsd.StatsClient(bigchaindb.config['graphite']['host'])

    federation = property(lambda self: set(self.nodes_except_me + [self.me]))
    """ Set of federation member public keys """

    def write_transaction(self, signed_transaction):
        """Write the transaction to bigchain.

        When first writing a transaction to the bigchain the transaction will be kept in a backlog until
        it has been validated by the nodes of the federation.

        Args:
            signed_transaction (Transaction): transaction with the `signature` included.

        Returns:
            dict: database response
        """
        signed_transaction = signed_transaction.to_dict()

        # we will assign this transaction to `one` node. This way we make sure that there are no duplicate
        # transactions on the bigchain
        if self.nodes_except_me:
            assignee = random.choice(self.nodes_except_me)
        else:
            # I am the only node
            assignee = self.me

        signed_transaction.update({'assignee': assignee})
        signed_transaction.update({'assignment_timestamp': time()})

        # write to the backlog
        return backend.query.write_transaction(self.connection, signed_transaction)

    def reassign_transaction(self, transaction):
        """Assign a transaction to a new node

        Args:
            transaction (dict): assigned transaction

        Returns:
            dict: database response or None if no reassignment is possible
        """

        other_nodes = tuple(
            self.federation.difference([transaction['assignee']])
        )
        new_assignee = random.choice(other_nodes) if other_nodes else self.me

        return backend.query.update_transaction(
                self.connection, transaction['id'],
                {'assignee': new_assignee, 'assignment_timestamp': time()})

    def delete_transaction(self, *transaction_id):
        """Delete a transaction from the backlog.

        Args:
            *transaction_id (str): the transaction(s) to delete

        Returns:
            The database response.
        """

        return backend.query.delete_transaction(self.connection, *transaction_id)

    def get_stale_transactions(self):
        """Get a cursor of stale transactions.

        Transactions are considered stale if they have been assigned a node, but are still in the
        backlog after some amount of time specified in the configuration
        """

        return backend.query.get_stale_transactions(self.connection, self.backlog_reassign_delay)

    def validate_transaction(self, transaction):
        """Validate a transaction.

        Args:
            transaction (Transaction): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.
        """

        return self.consensus.validate_transaction(self, transaction)

    def is_new_transaction(self, txid, exclude_block_id=None):
        """
        Return True if the transaction does not exist in any
        VALID or UNDECIDED block. Return False otherwise.

        Args:
            txid (str): Transaction ID
            exclude_block_id (str): Exclude block from search
        """
        block_statuses = self.get_blocks_status_containing_tx(txid)
        block_statuses.pop(exclude_block_id, None)
        for status in block_statuses.values():
            if status != self.BLOCK_INVALID:
                return False
        return True

    def get_block(self, block_id, include_status=False):
        """Get the block with the specified `block_id` (and optionally its status)

        Returns the block corresponding to `block_id` or None if no match is
        found.

        Args:
            block_id (str): transaction id of the transaction to get
            include_status (bool): also return the status of the block
                       the return value is then a tuple: (block, status)
        """
        # get block from database
        block_dict = backend.query.get_block(self.connection, block_id)
        # get the asset ids from the block
        if block_dict:
            asset_ids = Block.get_asset_ids(block_dict)
            # get the assets from the database
            assets = self.get_assets(asset_ids)
            # add the assets to the block transactions
            block_dict = Block.couple_assets(block_dict, assets)

        status = None
        if include_status:
            if block_dict:
                status = self.block_election_status(block_dict)
            return block_dict, status
        else:
            return block_dict

    def get_transaction(self, txid, include_status=False):
        """Get the transaction with the specified `txid` (and optionally its status)

        This query begins by looking in the bigchain table for all blocks containing
        a transaction with the specified `txid`. If one of those blocks is valid, it
        returns the matching transaction from that block. Else if some of those
        blocks are undecided, it returns a matching transaction from one of them. If
        the transaction was found in invalid blocks only, or in no blocks, then this
        query looks for a matching transaction in the backlog table, and if it finds
        one there, it returns that.

        Args:
            txid (str): transaction id of the transaction to get
            include_status (bool): also return the status of the transaction
                                   the return value is then a tuple: (tx, status)

        Returns:
            A :class:`~.models.Transaction` instance if the transaction
            was found in a valid block, an undecided block, or the backlog table,
            otherwise ``None``.
            If :attr:`include_status` is ``True``, also returns the
            transaction's status if the transaction was found.
        """

        response, tx_status = None, None

        blocks_validity_status = self.get_blocks_status_containing_tx(txid)
        check_backlog = True

        if blocks_validity_status:
            # Disregard invalid blocks, and return if there are no valid or undecided blocks
            blocks_validity_status = {
                _id: status for _id, status in blocks_validity_status.items()
                if status != Bigchain.BLOCK_INVALID
            }
            if blocks_validity_status:

                # The transaction _was_ found in an undecided or valid block,
                # so there's no need to look in the backlog table
                check_backlog = False

                tx_status = self.TX_UNDECIDED
                # If the transaction is in a valid or any undecided block, return it. Does not check
                # if transactions in undecided blocks are consistent, but selects the valid block
                # before undecided ones
                for target_block_id in blocks_validity_status:
                    if blocks_validity_status[target_block_id] == Bigchain.BLOCK_VALID:
                        tx_status = self.TX_VALID
                        break

                # Query the transaction in the target block and return
                response = backend.query.get_transaction_from_block(self.connection, txid, target_block_id)

        if check_backlog:
            response = backend.query.get_transaction_from_backlog(self.connection, txid)

            if response:
                tx_status = self.TX_IN_BACKLOG

        if response:
            if tx_status == self.TX_IN_BACKLOG:
                response = Transaction.from_dict(response)
            else:
                # If we are reading from the bigchain collection the asset is
                # not in the transaction so we need to fetch the asset and
                # reconstruct the transaction.
                response = Transaction.from_db(self, response)

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
        blocks = backend.query.get_blocks_status_from_transaction(self.connection, txid)
        if blocks:
            # Determine the election status of each block
            blocks_validity_status = {
                block['id']: self.block_election_status(block)
                for block in blocks
            }

            # NOTE: If there are multiple valid blocks with this transaction,
            # something has gone wrong
            if list(blocks_validity_status.values()).count(Bigchain.BLOCK_VALID) > 1:
                block_ids = str([
                    block for block in blocks_validity_status
                    if blocks_validity_status[block] == Bigchain.BLOCK_VALID
                ])
                raise core_exceptions.CriticalDoubleInclusion(
                    'Transaction {tx} is present in '
                    'multiple valid blocks: {block_ids}'
                    .format(tx=txid, block_ids=block_ids))

            return blocks_validity_status

        else:
            return None

    def get_asset_by_id(self, asset_id):
        """Returns the asset associated with an asset_id.

            Args:
                asset_id (str): The asset id.

            Returns:
                dict if the asset exists else None.
        """
        cursor = backend.query.get_asset_by_id(self.connection, asset_id)
        cursor = list(cursor)
        if cursor:
            return cursor[0]['asset']

    def get_spent(self, txid, output):
        """Check if a `txid` was already used as an input.

        A transaction can be used as an input for another transaction. Bigchain
        needs to make sure that a given `(txid, output)` is only used once.

        This method will check if the `(txid, output)` has already been
        spent in a transaction that is in either the `VALID`, `UNDECIDED` or
        `BACKLOG` state.

        Args:
            txid (str): The id of the transaction
            output (num): the index of the output in the respective transaction

        Returns:
            The transaction (Transaction) that used the `(txid, output)` as an
            input else `None`

        Raises:
            CriticalDoubleSpend: If the given `(txid, output)` was spent in
            more than one valid transaction.
        """
        # checks if an input was already spent
        # checks if the bigchain has any transaction with input {'txid': ...,
        # 'output': ...}
        transactions = list(backend.query.get_spent(self.connection, txid,
                                                    output))

        # a transaction_id should have been spent at most one time
        # determine if these valid transactions appear in more than one valid
        # block
        num_valid_transactions = 0
        non_invalid_transactions = []
        for transaction in transactions:
            # ignore transactions in invalid blocks
            # FIXME: Isn't there a faster solution than doing I/O again?
            _, status = self.get_transaction(transaction['id'],
                                             include_status=True)
            if status == self.TX_VALID:
                num_valid_transactions += 1
            # `txid` can only have been spent in at most on valid block.
            if num_valid_transactions > 1:
                raise core_exceptions.CriticalDoubleSpend(
                    '`{}` was spent more than once. There is a problem'
                    ' with the chain'.format(txid))
            # if its not and invalid transaction
            if status is not None:
                non_invalid_transactions.append(transaction)

        if non_invalid_transactions:
            return Transaction.from_dict(non_invalid_transactions[0])

        # Either no transaction was returned spending the `(txid, output)` as
        # input or the returned transactions are not valid.

    def get_owned_ids(self, owner):
        """Retrieve a list of ``txid`` s that can be used as inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
            pointing to another transaction's condition
        """
        return self.get_outputs_filtered(owner, spent=False)

    @property
    def fastquery(self):
        return fastquery.FastQuery(self.connection, self.me)

    def get_outputs_filtered(self, owner, spent=None):
        """
        Get a list of output links filtered on some criteria

        Args:
            owner (str): base58 encoded public_key.
            spent (bool): If ``True`` return only the spent outputs. If
                          ``False`` return only unspent outputs. If spent is
                          not specified (``None``) return all outputs.

        Returns:
            :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
            pointing to another transaction's condition
        """
        outputs = self.fastquery.get_outputs_by_public_key(owner)
        if spent is None:
            return outputs
        elif spent is True:
            return self.fastquery.filter_unspent_outputs(outputs)
        elif spent is False:
            return self.fastquery.filter_spent_outputs(outputs)

    def get_transactions_filtered(self, asset_id, operation=None):
        """
        Get a list of transactions filtered on some criteria
        """
        txids = backend.query.get_txids_filtered(self.connection, asset_id,
                                                 operation)
        for txid in txids:
            tx, status = self.get_transaction(txid, True)
            if status == self.TX_VALID:
                yield tx

    def create_block(self, validated_transactions):
        """Creates a block given a list of `validated_transactions`.

        Note that this method does not validate the transactions. Transactions
        should be validated before calling create_block.

        Args:
            validated_transactions (list(Transaction)): list of validated
                                                        transactions.

        Returns:
            Block: created block.
        """
        # Prevent the creation of empty blocks
        if not validated_transactions:
            raise exceptions.OperationError('Empty block creation is not '
                                            'allowed')

        voters = list(self.federation)
        block = Block(validated_transactions, self.me, gen_timestamp(), voters)
        block = block.sign(self.me_private)

        return block

    # TODO: check that the votings structure is correctly constructed
    def validate_block(self, block):
        """Validate a block.

        Args:
            block (Block): block to validate.

        Returns:
            The block if the block is valid else it raises and exception
            describing the reason why the block is invalid.
        """
        return self.consensus.validate_block(self, block)

    def has_previous_vote(self, block_id):
        """Check for previous votes from this node

        Args:
            block_id (str): the id of the block to check

        Returns:
            bool: :const:`True` if this block already has a
            valid vote from this node, :const:`False` otherwise.

        """
        votes = list(backend.query.get_votes_by_block_id_and_voter(self.connection, block_id, self.me))
        el, _ = self.consensus.voting.partition_eligible_votes(votes, [self.me])
        return bool(el)

    def write_block(self, block):
        """Write a block to bigchain.

        Args:
            block (Block): block to write to bigchain.
        """

        # Decouple assets from block
        assets, block_dict = block.decouple_assets()
        # write the assets
        if assets:
            self.write_assets(assets)

        # write the block
        return backend.query.write_block(self.connection, block_dict)

    def prepare_genesis_block(self):
        """Prepare a genesis block."""

        metadata = {'message': 'Hello World from the BigchainDB'}
        transaction = Transaction.create([self.me], [([self.me], 1)],
                                         metadata=metadata)

        # NOTE: The transaction model doesn't expose an API to generate a
        #       GENESIS transaction, as this is literally the only usage.
        transaction.operation = 'GENESIS'
        transaction = transaction.sign([self.me_private])

        # create the block
        return self.create_block([transaction])

    def create_genesis_block(self):
        """Create the genesis block

        Block created when bigchain is first initialized. This method is not atomic, there might be concurrency
        problems if multiple instances try to write the genesis block when the BigchainDB Federation is started,
        but it's a highly unlikely scenario.
        """

        # 1. create one transaction
        # 2. create the block with one transaction
        # 3. write the block to the bigchain

        blocks_count = backend.query.count_blocks(self.connection)

        if blocks_count:
            raise exceptions.GenesisBlockAlreadyExistsError('Cannot create the Genesis block')

        block = self.prepare_genesis_block()
        self.write_block(block)

        return block

    def vote(self, block_id, previous_block_id, decision, invalid_reason=None):
        """Create a signed vote for a block given the
        :attr:`previous_block_id` and the :attr:`decision` (valid/invalid).

        Args:
            block_id (str): The id of the block to vote on.
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
            'timestamp': gen_timestamp()
        }

        vote_data = serialize(vote)
        signature = crypto.PrivateKey(self.me_private).sign(vote_data.encode())

        vote_signed = {
            'node_pubkey': self.me,
            'signature': signature.decode(),
            'vote': vote
        }

        return vote_signed

    def write_vote(self, vote):
        """Write the vote to the database."""
        return backend.query.write_vote(self.connection, vote)

    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        last_block_id = backend.query.get_last_voted_block_id(self.connection,
                                                              self.me)
        return Block.from_dict(self.get_block(last_block_id))

    def block_election(self, block):
        if type(block) != dict:
            block = block.to_dict()
        votes = list(backend.query.get_votes_by_block_id(self.connection,
                                                         block['id']))
        return self.consensus.voting.block_election(block, votes,
                                                    self.federation)

    def block_election_status(self, block):
        """Tally the votes on a block, and return the status:
           valid, invalid, or undecided."""
        return self.block_election(block)['status']

    def get_assets(self, asset_ids):
        """
        Return a list of assets that match the asset_ids

        Args:
            asset_ids (:obj:`list` of :obj:`str`): A list of asset_ids to
                retrieve from the database.

        Returns:
            list: The list of assets returned from the database.
        """
        return backend.query.get_assets(self.connection, asset_ids)

    def write_assets(self, assets):
        """
        Writes a list of assets into the database.

        Args:
            assets (:obj:`list` of :obj:`dict`): A list of assets to write to
                the database.
        """
        return backend.query.write_assets(self.connection, assets)

    def text_search(self, search, *, limit=0):
        """
        Return an iterator of assets that match the text search

        Args:
            search (str): Text search string to query the text index
            limit (int, optional): Limit the number of returned documents.

        Returns:
            iter: An iterator of assets that match the text search.
        """
        assets = backend.query.text_search(self.connection, search, limit=limit)

        # TODO: This is not efficient. There may be a more efficient way to
        #       query by storing block ids with the assets and using fastquery.
        #       See https://github.com/bigchaindb/bigchaindb/issues/1496
        for asset in assets:
            tx, status = self.get_transaction(asset['id'], True)
            if status == self.TX_VALID:
                yield asset
