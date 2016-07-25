import time

from multipipes import Pipe
from bigchaindb.pipelines import utils


def test_changefeed(b, user_vk):
    outpipe = Pipe()
    changefeed = utils.ChangeFeed('backlog', 'insert', prefeed=[1, 2, 3])
    changefeed.outqueue = outpipe
    changefeed.start()
    time.sleep(1)
    changefeed.terminate()

    assert outpipe.qsize() == 3
