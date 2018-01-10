import os
import json
import time
import uuid

import kubernetes.client
from kubernetes.client.rest import ApiException


MINIKUBE_URI = 'https://127.0.0.1:8443'
MINIKUBE_HOME = os.environ.get('MINIKUBE_HOME', os.environ['HOME'])
# TODO: create a default pod spec of BDB
BDB_POD_SPEC = {}


class Node():

    def __init__(self, namespace='itest-api', name=None, spec=BDB_POD_SPEC):
        config = kubernetes.client.Configuration()
        config.host = MINIKUBE_URI
        config.key_file = os.path.join(MINIKUBE_HOME, '.minikube/client.key')
        config.cert_file = os.path.join(MINIKUBE_HOME, '.minikube/client.crt')
        config.verify_ssl = False
        self.api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(config))
        self.namesapce = namespace
        self.name = name or uuid.uuid4().hex
        self.uri = None

        pod = kubernetes.client.V1Pod()
        pod.version = 'v1'
        pod.kind = 'Pod'
        pod.metadata = {"name": self.name}
        pod.spec = {"containers": [{"name": "myapp-container",
                                    "image": "busybox",
                                    "command": ["sh", "-c", "echo Hello Kubernetes! && sleep 3600"]}]}
        self.pod = pod

    def start(self, return_after_running=True):
        """ Start node."""
        try:
            self.api_instance.create_namespaced_pod(self.namesapce, self.pod)
            if return_after_running:
                for i in range(1, 20):
                    if self.is_running:
                        break
                    time.sleep(1)
        except ApiException as e:
            pass

    def stop(self, return_after_stopping=True):
        """ Stop node."""
        body = kubernetes.client.V1DeleteOptions()
        body.api_version = 'v1'
        self.api_instance.delete_namespaced_pod(self.name, self.namespace, body)
        if return_after_stopping:
            for i in range(1, 20):
                if self.is_running:
                    break
                time.sleep(1)

    @property
    def is_running(self):
        """Get the current status of node"""
        resp = self.api_instance.read_namespaced_pod(self.name, self.namespace, exact=True)
        if resp['status']['phase'] == 'Running':
            return True
        else:
            return False

    @property
    def uri(self):
        if self.is_running:
            resp = self.api_instance.read_namespaced_pod(self.name, self.namespace, exact=True)
            return resp['status']['pod_ip']
        else:
            return False

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
