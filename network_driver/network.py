import random
import json
import uuid
import copy
import time

from node import Node

CHAIN_GENESIS = {"genesis_time": "0001-01-01T00:00:00Z",
                 "chain_id": "",
                 "validators": [],
                 "app_hash": ""}


class Network():

    def __init__(self, max_size=1, namespace='default', chain_id=None):
        # NOTE: a maximum of 19 validators can be allocated
        self.max_size = max_size
        self.priv_validator_list = load_validators(max_size)
        self.namespace = namespace
        self.genesis = copy.deepcopy(CHAIN_GENESIS)
        self.genesis['chain_id'] = chain_id or uuid.uuid4().hex
        self.genesis['validators'] = [extract_validator(v) for v in self.priv_validator_list]
        self.nodes = []

        for i in range(0, max_size):
            self.nodes.append(Node(self.priv_validator_list[i], self.genesis, self.namespace))

    def ensure_started(self, n=None, concurrent=True):
        """ Ensure that n nodes of the network are running
            NOTE: In order for the network to work properly 2/3 of the nodes
                  should be operational
        """
        if n is None:
            n = self.max_size

        n = min(n, self.max_size)
        for i in range(0, n):
            if not self.nodes[i].is_running:
                self.nodes[i].start(not concurrent)

        nodes_online = 0
        while concurrent:
            if nodes_online == n:
                break

            for i in range(0, n):
                if self.nodes[i].is_running:
                    nodes_online += 1

            time.sleep(1)

    def stop(self, n=None):
        if n is None:
            n = self.max_size

        for i in range(0, n):
            self.nodes[i].stop()


def load_validators(count):
    with open('validators.json') as json_data:
        return random.sample(json.load(json_data), count)


def extract_validator(priv_validator):
    return {"pub_key": priv_validator['pub_key'],
            "power": 10,
            "name": ""}
