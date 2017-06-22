# How to Install the Latest pip and setuptools

You can check the version of `pip` you're using (in your current virtualenv) by doing:
```text
pip -V
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less than 3.5, then you must install a `pip` version associated with Python 3.5+. In the following instructions, we call it `pip3` but you may be able to use `pip` if that refers to the same thing. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/).

On Ubuntu 16.04, we found that this works:
```text
sudo apt-get install python3-pip
```

That should install a Python 3 version of `pip` named `pip3`. If that didn't work, then another way to get `pip3` is to do `sudo apt-get install python3-setuptools` followed by `sudo easy_install3 pip`.

You can upgrade `pip` (`pip3`) and `setuptools` to the latest versions using:
```text
pip3 install --upgrade pip setuptools
```
