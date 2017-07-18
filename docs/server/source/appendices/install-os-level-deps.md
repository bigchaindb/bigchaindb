# How to Install OS-Level Dependencies

BigchainDB Server has some OS-level dependencies that must be installed.

On Ubuntu 16.04, we found that the following was enough:
```text
sudo apt-get update
sudo apt-get install libffi-dev libssl-dev
```

On Fedora 23–25, we found that the following was enough:
```text
sudo dnf update
sudo dnf install gcc-c++ redhat-rpm-config python3-devel libffi-devel
```

(If you're using a version of Fedora before version 22, you may have to use `yum` instead of `dnf`.)
