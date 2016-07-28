import time
import random
from unittest.mock import patch

import rethinkdb as r

from bigchaindb.pipelines import election
from multipipes import Pipe, Pipeline


def test_check_for_quorum(b, user_vk):
    e = election.Election()


def test_check_requeue_transaction(b, user_vk):
    pass

