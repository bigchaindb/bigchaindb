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

- Get a text editor. Internally, we like:

  - Vim
  - PyCharm
  - Visual Studio Code
  - Atom
  - GNU Emacs (Trent is crazy)
  - GNU nano (Troy has lost his mind)

- If you plan to do JavaScript coding, get the latest JavaScript stuff (npm etc.).

- If you plan to do Python codding, get `the latest Python <https://www.python.org/downloads/>`_, and
  get the latest ``pip``.

.. warning:: 

   Don't use apt or apt-get to get the latest ``pip``. It won't work properly. Use ``get-pip.py``
   from `the pip website <https://pip.pypa.io/en/stable/installing/>`_.

- Use the latest ``pip`` to get the latest ``virtualenv`` and ``pre-commit``:

  .. code::

     $ pip install virtualenv
     $ pip install pre-commit


Start Coding
------------

Use the Git `Fork and Pull Request Workflow <https://github.com/susam/gitpr>`_. Tip: print that page for reference.

Your Python code should follow `our Python Style Guide <https://github.com/bigchaindb/bigchaindb/blob/master/PYTHON_STYLE_GUIDE.md>`_.
Similarly for JavaScript.

Make sure `pre-commit <https://pre-commit.com/>`_ actually checks commits. Do:

  .. code::

     $ pre-commit install


The Tricky Bits
---------------

Running MongoDB and Tendermint to test stuff...

But how? 

You can look up how to install them, configure them, and run them. But the details are hazy.

This is where we need some advice and help.

Vanshdeep was going to write what he does. TODO: add that here.

What about a multi-node setup? Even more confusing.


Run the Tests Locally
---------------------

This is also unclear. I mean, use pytest, but how, exactly? Again MongoDB and Tendermint are probably needed sometimes.


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

You are awesome. We will send swag if you let us. Do you want a job? Apply! Berlin is great. Meet the pandas. Say hi to Angela Merkel. Walk along the Under den Linden. See where Einstein and Planck taught university. Contemplate the speed of light on the actual Potsdamer Platz platform.

See the former location of the telescope that first revealed the planet Neptune to human eyes. (The telescope is now in Munich.) Fresh spargel in the spring! Fresh kurbis in the fall! Rain all winter. The weather is perfect. You will love it.

`Unsplash photos of Berlin <https://unsplash.com/search/photos/berlin>`_



