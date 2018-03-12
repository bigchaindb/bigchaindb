Write Code
==========

What are you Doing???
---------------------

If you want to resolve an issue, then find one that is open and unresolved.

If you want to implement a BEP, then pick one you believe you can implement. You can ask for help, but not to do *everything*.
All BEPs are in the `bigchaindb/BEPs <https://github.com/bigchaindb/BEPs>`_ repository on GitHub.

Tell us what you're doing so we don't do it too. You can tell us on Gitter or by email.


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


Running a Local Node for Dev and Test
-------------------------------------

This is tricky and personal. Different people do it different ways. We documented some of those on separate pages.

- `Vanshdeep's notes on dev node setup and running all tests locally <vanshdeep-notes.html>`_
- More to come? (Potentially: using Docker Compose, Kubernetes and Minikube, or Ansible.)


Create the PR on GitHub
-----------------------

Git push your branch to GitHub so as to create a pull request against the branch where the code you want to change *lives*.

Travis and Codecov will run and might complain. Look into the complaints and fix them before merging.


First-Time Pull Requests from External Users
--------------------------------------------

First-time pull requests from external users who haven't contributed before will get blocked by the requirement to agree to the
BigchainDB Contributor License Agreement (CLA). It doesn't take long to agree to it. Go to
`https://www.bigchaindb.com/cla/ <https://www.bigchaindb.com/cla/>`_ and:

- Select the CLA you want to agree to (for individuals or for a whole company)
- Fill in the form and submit it
- Wait for an email from us with the next step. There is only one: copying a special block of text to GitHub.


Merge!
------

Ideally, we like your PR and merge it right away. We don't want to keep you waiting.

If we want to make changes, we'll do them in a follow-up PR.

-----------------

You are awesome. We will send swag if you let us. Do you want a job? Apply! Berlin is great. Meet the pandas. Say hi to Angela Merkel. Walk along the Unter den Linden. See where Einstein and Planck taught university. Contemplate the speed of light on the actual Potsdamer Platz platform.

See the former location of the telescope that first revealed the planet Neptune to human eyes. (The telescope is now in Munich.) Fresh spargel in the spring! Fresh kurbis in the fall! Rain all winter. The weather is perfect. You will love it.

`Unsplash photos of Berlin <https://unsplash.com/search/photos/berlin>`_



