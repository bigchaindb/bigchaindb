import json
import time
import uuid
import copy

import kubernetes
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream


# TODO: create a default pod spec of BDB
MONGODB_SPEC = {"name": "mongodb",
                "image": "mongodb:bdb-itest"}
TENDERMINT_SPEC = {"name": "tendermint",
                   "image": "tendermint:bdb-itest",
                   "command": ["/bin/bash"],
                   "args": ["-c",  "./tendermint_entrypoint.sh '{}' '{}'"],
                   "ports": [{"containerPort": 46656},
                             {"containerPort": 46657}]}
BIGCHAINDB_SPEC = {"name": "bigchaindb",
                   "image": "bigchaindb:bdb-itest",
                   "ports": [{"containerPort": 9984}]}


class Node():

    def __init__(self, tendermint_priv_validator=None, tendermint_genesis=None,
                 namespace='default', name=None):

        kubernetes.config.load_kube_config()
        config = kubernetes.client.Configuration()
        config.assert_hostname = False
        kubernetes.client.Configuration.set_default(config)

        self.api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(config))
        self.namespace = namespace
        self.name = name or uuid.uuid4().hex

        pod = kubernetes.client.V1Pod()
        pod.version = 'v1'
        pod.kind = 'Pod'
        pod.metadata = {"name": self.name}

        tendermint_spec = copy.deepcopy(TENDERMINT_SPEC)
        [arg, command] = tendermint_spec["args"]
        command = command.format(json.dumps(tendermint_priv_validator),
                                 json.dumps(tendermint_genesis))
        tendermint_spec["args"] = [arg, command]

        pod.spec = {"containers": [MONGODB_SPEC,
                                   tendermint_spec,
                                   BIGCHAINDB_SPEC]}
        self.pod = pod

    def start(self, return_after_running=True):
        """ Start node."""
        try:
            self.api_instance.create_namespaced_pod(self.namespace, self.pod)
            if return_after_running:
                for i in range(1, 3600):
                    if self.is_running:
                        break
                    time.sleep(1)
        except ApiException as e:
            raise e

    def stop(self, return_after_stopping=True):
        """ Stop node."""
        if self.is_running:
            body = kubernetes.client.V1DeleteOptions()
            body.api_version = 'v1'
            body.grace_period_seconds = 0
            self.api_instance.delete_namespaced_pod(self.name, self.namespace, body)
            if return_after_stopping:
                for i in range(1, 20):
                    if not self.is_running:
                        break
                    time.sleep(1)

    def reset(self):
        self.stop_tendermint()
        self.stop_bigchaindb()
        self._exec_command('tendermint', 'tendermint unsafe_reset_all')
        self._exec_command('bigchaindb', 'bigchaindb -y drop')
        self.start_tendermint()
        self.start_bigchaindb()

    @property
    def is_running(self):
        """Get the current status of node"""
        try:
            resp = self.api_instance.read_namespaced_pod(self.name, self.namespace, exact=True)
            if resp.status.phase == 'Running':
                return True
            else:
                return False
        except ApiException as e:
            return False

    @property
    def uri(self):
        if self.is_running:
            resp = self.api_instance.read_namespaced_pod(self.name, self.namespace, exact=True)
            return resp.status.pod_ip
        else:
            return False

    def stop_tendermint(self):
        self._exec_command('tendermint', 'pkill tendermint')

    def start_tendermint(self):
        self._exec_command('tendermint', 'tendermint node --proxy_app=dummy', tty=True)

    def reset_tendermint(self):
        self.stop_tendermint()
        self._exec_command('tendermint', 'tendermint unsafe_reset_all')
        self.start_tendermint()

    def stop_db(self):
        self._exec_command('mongodb', 'pkill mongod')

    def start_db(self):
        self._exec_command('mongodb', 'mongod', tty=True)

    def start_bigchaindb(self):
        self._exec_command('bigchaindb', 'bigchaindb start', tty=True)

    def stop_bigchaindb(self):
        self._exec_command('bigchaindb', 'pkill bigchaindb')

    def reset_bigchaindb(self):
        self.stop_bigchaindb()
        self._exec_command('bigchaindb', 'bigchaindb -y drop')
        self.start_bigchaindb()

    def _exec_command(self, container, command, stdout=True, tty=False):
        try:
            exec_command = ['/bin/bash', '-c', command]
            resp = stream(self.api_instance.connect_post_namespaced_pod_exec,
                          self.name,
                          self.namespace,
                          container=container,
                          command=exec_command,
                          stderr=False, stdin=False, stdout=stdout, tty=tty)
            return resp
        except ApiException as e:
            print("Exception when executing command: %s\n" % e)

    def _create_namespace(self, namespace):
        namespace_spec = kubernetes.client.V1Namespace()
        namespace_spec.api_version = 'v1'
        namespace_spec.metadata = {'name': namespace}

        try:
            self.api_instance.create_namespace(namespace_spec)
            return True
        except ApiException as e:
            resp_body = json.loads(e.body)
            if resp_body.reason == 'AlreadyExists':
                return True
            else:
                raise e
