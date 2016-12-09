
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
