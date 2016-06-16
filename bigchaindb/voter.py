import logging
import multiprocessing as mp
import ctypes

from bigchaindb import Bigchain
from bigchaindb.monitor import Monitor


logger = logging.getLogger(__name__)


class BlockStream(object):
    """
    Combine the stream of new blocks coming from the changefeed with the list of unvoted blocks.

    This is a utility class that abstracts the source of data for the `Voter`.
    """

    def __init__(self, new_blocks):
        """
        Create a new BlockStream instance.

        Args:
            new_block (queue): a queue of new blocks
        """

        b = Bigchain()
        self.new_blocks = new_blocks
        # TODO: there might be duplicate blocks since we *first* get the changefeed and only *then* we query the
        #       database to get the old blocks.

        # TODO how about a one liner, something like:
        # self.unvoted_blocks = b.get_unvoted_blocks() if not b.nodes_except_me else []
        self.unvoted_blocks = []
        if not b.nodes_except_me:
            self.unvoted_blocks = b.get_unvoted_blocks()

    def get(self):
        """
        Return the next block to be processed.
        """
        try:
            # FIXME: apparently RethinkDB returns a list instead of a cursor when using `order_by`.
            #        We might change the `pop` in the future, when the driver will return a cursor.
            #        We have a test for this, so if the driver implementation changes we will get a failure:
            #        - tests/test_voter.py::TestBlockStream::test_if_old_blocks_get_should_return_old_block_first
            return self.unvoted_blocks.pop(0)
        except IndexError:
            return self.new_blocks.get()


class Voter(object):

    def __init__(self, q_new_block):
        """
        Initialize the class with the needed queues.

        Initialize with a queue where new blocks added to the bigchain will be put
        """

        self.monitor = Monitor()

        self.q_new_block = q_new_block
        self.q_blocks_to_validate = mp.Queue()
        self.q_validated_block = mp.Queue()
        self.q_voted_block = mp.Queue()
        self.v_previous_block_id = mp.Value(ctypes.c_char_p)
        self.v_previous_block_number = mp.Value(ctypes.c_uint64)
        self.initialized = mp.Event()

    def feed_blocks(self):
        """
        Prepare the queue with blocks to validate
        """

        block_stream = BlockStream(self.q_new_block)
        while True:
            # poison pill
            block = block_stream.get()
            if block == 'stop':
                self.q_blocks_to_validate.put('stop')
                return

            self.q_blocks_to_validate.put(block)

    def validate(self):
        """
        Checks if incoming blocks are valid or not
        """

        # create a bigchain instance. All processes should create their own bigchcain instance so that they all
        # have their own connection to the database
        b = Bigchain()

        logger.info('voter waiting for new blocks')
        # signal initialization complete
        self.initialized.set()

        while True:
            new_block = self.q_blocks_to_validate.get()

            # poison pill
            if new_block == 'stop':
                self.q_validated_block.put('stop')
                return

            logger.info('new_block arrived to voter')
            block_number = self.v_previous_block_number.value + 1

            with self.monitor.timer('validate_block'):
                validity = b.is_valid_block(new_block)

            self.q_validated_block.put((new_block,
                                        self.v_previous_block_id.value.decode(),
                                        block_number,
                                        validity))

            self.v_previous_block_id.value = new_block['id'].encode()
            self.v_previous_block_number.value = block_number

    def vote(self):
        """
        Votes on the block based on the decision of the validation
        """

        # create a bigchain instance
        b = Bigchain()

        while True:
            elem = self.q_validated_block.get()

            # poison pill
            if elem == 'stop':
                self.q_voted_block.put('stop')
                return

            validated_block, previous_block_id, block_number, decision = elem
            vote = b.vote(validated_block, previous_block_id, decision)
            self.q_voted_block.put((validated_block, vote, block_number))

    def update_block(self):
        """
        Appends the vote in the bigchain table
        """

        # create a bigchain instance
        b = Bigchain()

        while True:
            elem = self.q_voted_block.get()

            # poison pill
            if elem == 'stop':
                logger.info('clean exit')
                return

            block, vote, block_number = elem
            logger.info('updating block %s with number %s and with vote %s', block['id'], block_number, vote)
            b.write_vote(block, vote, block_number)

    def bootstrap(self):
        """
        Before starting handling the new blocks received by the changefeed we need to handle unvoted blocks
        added to the bigchain while the process was down

        We also need to set the previous_block_id and the previous block_number
        """

        b = Bigchain()
        last_voted = b.get_last_voted_block()

        self.v_previous_block_number.value = last_voted['block_number']
        self.v_previous_block_id.value = last_voted['id'].encode()

    def kill(self):
        """
        Terminate processes
        """
        self.q_new_block.put('stop')

    def start(self):
        """
        Initialize, spawn, and start the processes
        """

        self.bootstrap()

        # initialize the processes
        p_feed_blocks = mp.Process(name='block_feeder', target=self.feed_blocks)
        p_validate = mp.Process(name='block_validator', target=self.validate)
        p_vote = mp.Process(name='block_voter', target=self.vote)
        p_update = mp.Process(name='block_updater', target=self.update_block)

        # start the processes
        p_feed_blocks.start()
        p_validate.start()
        p_vote.start()
        p_update.start()


class Election(object):

    def __init__(self, q_block_new_vote):
        """
        Initialize the class with the needed queues.

        Initialize a queue where blocks with new votes will be held
        """
        self.q_block_new_vote = q_block_new_vote
        self.q_invalid_blocks = mp.Queue()

    def check_for_quorum(self):
        """
        Checks if block has enough invalid votes to make a decision
        """
        b = Bigchain()

        while True:
            next_block = self.q_block_new_vote.get()

            # poison pill
            if next_block == 'stop':
                self.q_invalid_blocks.put('stop')
                logger.info('clean exit')
                return

            if b.block_election_status(next_block) == 'invalid':
                self.q_invalid_blocks.put(next_block)

    def requeue_transactions(self):
        """
        Liquidates transactions from invalid blocks so they can be processed again
        """
        while True:
            invalid_block = self.q_invalid_blocks.get()

            # poison pill
            if invalid_block == 'stop':
                logger.info('clean exit')
                return

            b = Bigchain()
            for tx in invalid_block['block']['transactions']:
                b.write_transaction(tx)

    def kill(self):
        """
        Terminate processes
        """
        self.q_block_new_vote.put('stop')

    def start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_quorum_check = mp.Process(name='check_for_quorum', target=self.check_for_quorum)
        p_requeue_tx = mp.Process(name='requeue_tx', target=self.requeue_transactions)

        # start the processes
        p_quorum_check.start()
        p_requeue_tx.start()
