from bigchaindb.db.utils import Connection

class RethinkDBBackend:

    def __init__(self, host=None, port=None, dbname=None):
        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.dbname = dbname or bigchaindb.config['database']['name']

    @property
    def conn(self):
        if not self._conn:
            self._conn = self.reconnect()
        return self._conn

    def write_transaction(self, signed_transaction, durability='soft'):
        # write to the backlog
        response = self.connection.run(
                r.table('backlog')
                .insert(signed_transaction, durability=durability))


    def write_vote(self, vote):
        """Write the vote to the database."""

        self.connection.run(
                r.table('votes')
                .insert(vote))

    def write_block(self, block, durability='soft'):
        self.connection.run(
                r.table('bigchain')
                .insert(r.json(block.to_str()), durability=durability))

    def create_genesis_block(self):
        blocks_count = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .count())


    def get_transaction(self, txid, include_status=False):
        if validity:
                # Query the transaction in the target block and return
                response = self.connection.run(
                        r.table('bigchain', read_mode=self.read_mode)
                        .get(target_block_id)
                        .get_field('block')
                        .get_field('transactions')
                        .filter(lambda tx: tx['id'] == txid))[0]

        else:
            # Otherwise, check the backlog
            response = self.connection.run(r.table('backlog')
                                           .get(txid)
                                           .without('assignee', 'assignment_timestamp')
                                           .default(None))

    def get_tx_by_payload_uuid(self, payload_uuid):
        cursor = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(payload_uuid, index='payload_uuid')
                .concat_map(lambda block: block['block']['transactions'])
                .filter(lambda transaction: transaction['transaction']['data']['uuid'] == payload_uuid))

    def get_spent(self, txid, cid):
        response = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda transaction: transaction['transaction']['fulfillments']
                    .contains(lambda fulfillment: fulfillment['input'] == {'txid': txid, 'cid': cid})))

    def get_owned_ids(self, owner):
        response = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda tx: tx['transaction']['conditions']
                    .contains(lambda c: c['owners_after']
                        .contains(owner))))



    def get_last_voted_block(self):
        """Returns the last block that this node voted on."""

        try:
            # get the latest value for the vote timestamp (over all votes)
            max_timestamp = self.connection.run(
                    r.table('votes', read_mode=self.read_mode)
                    .filter(r.row['node_pubkey'] == self.me)
                    .max(r.row['vote']['timestamp']))['vote']['timestamp']

            last_voted = list(self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .filter(r.row['vote']['timestamp'] == max_timestamp)
                .filter(r.row['node_pubkey'] == self.me)))

        except r.ReqlNonExistenceError:
            # return last vote if last vote exists else return Genesis block
            res = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .filter(util.is_genesis_block))
            block = list(res)[0]
            return Block.from_dict(block)

        res = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get(last_block_id))

    def get_unvoted_blocks(self):
        """Return all the blocks that have not been voted on by this node.

        Returns:
            :obj:`list` of :obj:`dict`: a list of unvoted blocks
        """

        unvoted = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .filter(lambda block: r.table('votes', read_mode=self.read_mode)
                    .get_all([block['id'], self.me], index='block_and_voter')
                    .is_empty())
                .order_by(r.asc(r.row['block']['timestamp'])))

    def block_election_status(self, block_id, voters):
        """Tally the votes on a block, and return the status: valid, invalid, or undecided."""

        votes = self.connection.run(r.table('votes', read_mode=self.read_mode)
            .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter'))


    def search_block_election_on_index(self, value, index):
        response = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(value, index=index)
                .pluck('votes', 'id', {'block': ['voters']}))

    def has_previous_vote(self, block_id, voters):
        votes = list(self.connection.run(
            r.table('votes', read_mode=self.read_mode)
            .get_all([block_id, self.me], index='block_and_voter')))
