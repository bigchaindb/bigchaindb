
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Write Code
==========

Know What You Want to Write Code to Do
--------------------------------------

Do you want to write code to resolve an open issue (bug)? Which one?

Do you want to implement a BigchainDB Enhancement Proposal (BEP)? Which one?

You should know why you want to write code before you go any farther.


Refresh Yourself about the C4 Process
-------------------------------------

C4 is the Collective Code Construction Contract. It's quite short:
`re-reading it will only take a few minutes <https://github.com/bigchaindb/BEPs/tree/master/1>`_.


Set Up Your Local Machine. Here's How.
--------------------------------------

- Make sure you have Git installed.

- Get a text editor. Internally, we like:

  - Vim
  - PyCharm
  - Visual Studio Code
  - Atom
  - GNU Emacs (Trent is crazy)
  - GNU nano (Troy has lost his mind)

- If you plan to do JavaScript coding, get the latest JavaScript stuff (npm etc.).

- If you plan to do Python coding, get `the latest Python <https://www.python.org/downloads/>`_, and
  get the latest ``pip``.

.. warning:: 

   Don't use apt or apt-get to get the latest ``pip``. It won't work properly. Use ``get-pip.py``
   from `the pip website <https://pip.pypa.io/en/stable/installing/>`_.

- Use the latest ``pip`` to get the latest ``virtualenv``:

  .. code::

     $ pip install virtualenv

- Create a Python Virttual Environment (virtualenv) for doing BigchainDB Server development. There are many ways to do that. Google around and pick one.
  An old-fashioned but fine way is:
  
  .. code::

     $ virtualenv -p $(which python3.6) NEW_ENV_NAME
     $ . NEW_ENV_NAME/bin/activate

  Be sure to use Python 3.6.x as the Python version for your virtualenv. The virtualenv creation process will actually get the
  latest ``pip``, ``wheel`` and ``setuptools`` and put them inside the new virtualenv.


Before You Start Writing Code
-----------------------------

Read `BEP-24 <https://github.com/bigchaindb/BEPs/tree/master/24>`_
so you know what to do to ensure that your changes (i.e. your future pull request) can be merged.
It's easy and will save you some hassle later on.


Start Writing Code
------------------

Use the Git `Fork and Pull Request Workflow <https://github.com/susam/gitpr>`_. Tip: You could print that page for reference.

Your Python code should follow `our Python Style Guide <https://github.com/bigchaindb/bigchaindb/blob/master/PYTHON_STYLE_GUIDE.md>`_.
Similarly for JavaScript.

Make sure `pre-commit <https://pre-commit.com/>`_ actually checks commits. Do:

  .. code::

     $ pip install pre-commit  # might not do anything if it is already installed, which is okay
     $ pre-commit install

That will load the pre-commit settings in the file ``.pre-commit-config.yaml``. Now every time you do ``git commit <stuff>``, pre-commit
will run all those checks.

To install BigchainDB Server from the local code, and to keep it up to date with the latest code in there, use:

  .. code::

     $ pip install -e .[dev]

The ``-e`` tells it to use the latest code. The ``.`` means use the current directory, which should be the one containing ``setup.py``. 
The ``[dev]`` tells it to install some extra Python packages. Which ones? Open ``setup.py`` and look for ``dev`` in the ``extras_require`` section.


Remember to Write Tests
-----------------------

We like to test everything, if possible. Unit tests and also integration tests. We use the `pytest <https://docs.pytest.org/en/latest/>`_
framework to write Python tests. Read all about it.

Most tests are in the ``tests/`` folder. Take a look around.


Running a Local Node/Network for Dev and Test
---------------------------------------------

This is tricky and personal. Different people do it different ways. We documented some of those on separate pages:

- `Dev node setup and running all tests with Docker Compose <run-node-with-docker-compose.html>`_
- `Dev node setup and running all tests as processes <run-node-as-processes.html>`_
- `Dev network setup with stack.sh <run-dev-network-stack.html>`_
- `Dev network setup with Ansible <run-dev-network-ansible.html>`_
- More to come?


Create the PR on GitHub
-----------------------

Git push your branch to GitHub so as to create a pull request against the branch where the code you want to change *lives*.

Travis and Codecov will run and might complain. Look into the complaints and fix them before merging.
Travis gets its configuration and setup from the files:

- Some environment variables, if they are used. See https://docs.travis-ci.com/user/environment-variables/ 
- ``.travis.yml``
- ``tox.ini`` - What is tox? See `tox.readthedocs.io <https://tox.readthedocs.io/en/latest/>`_
- ``.ci/``  (as in Travis CI = Continuous Integration)

  - ``travis-after-success.sh``
  - ``travis-before-install.sh``
  - ``travis-before-script.sh``
  - ``travis-install.sh``
  - ``travis_script.sh``

Read about the `Travis CI build lifecycle <https://docs.travis-ci.com/user/customizing-the-build/>`_ to understand when those scripts run and what they do.
You can have even more scripts!

Codecov gets its configuration from the file `codeocov.yaml <https://github.com/codecov/support/wiki/Codecov-Yaml>`_ which is also documented at
`docs.codecov.io <https://docs.codecov.io/v4.3.6/docs/codecov-yaml>`_. Codecov might also use ``setup.cfg``.


Merge!
------

Ideally, we like your PR and merge it right away. We don't want to keep you waiting.

If we want to make changes, we'll do them in a follow-up PR.
