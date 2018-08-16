# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


import subprocess


def test_build_server_docs():
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE)
    proc.stdin.write('cd docs/server; make html'.encode())
    proc.stdin.close()
    assert proc.wait() == 0


def test_build_root_docs():
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE)
    proc.stdin.write('cd docs/root; make html'.encode())
    proc.stdin.close()
    assert proc.wait() == 0
