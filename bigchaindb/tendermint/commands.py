from abci import ABCIServer

from bigchaindb.tendermint.core import App


def start():
    app = ABCIServer(app=App())
    app.run()


if __name__ == '__main__':
    start()
