Development
===========

Have a great idea for a new feature? Want to fix a bug? Then, this guide is for you!

Prerequisites
-------------

These instructions assume that you have the following things available.

* Python 2.6 - 2.7 or Python 3.3 - Python 3.4
* The virtualenv_ tool
* The pip_ tool
* Git_

Environment Setup
-----------------

First, fork_ the Warthog Client on GitHub.

Check out your fork of the source code.

.. code-block:: bash

    $ git clone https://github.com/you/warthog.git

Create and set up a branch for your awesome new feature or bug fix.

.. code-block:: bash

    $ cd warthog
    $ git checkout -b feature-xyz
    $ git push origin feature-xyz:feature-xyz
    $ git branch -u origin/feature-xyz

Set up a virtual environment.

.. code-block:: bash

    $ virtualenv env

Enter the virtualenv install required dependencies.

.. code-block:: bash

    $ source env/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt

Install the checkout in "development mode".

.. code-block:: bash

    $ pip install -e .

Contributing
------------

Next, code up your feature or bug fix and create a `pull request`_. Some things to keep in
mind when submitting a pull request are listed below.

* Your pull request should be a single commit that adds only a single feature or fixes only
  a single bug. Take a look at this post that describes squashing_ all your commits into only
  a single commit, or, the Github documentation on rebasing_.

* If you've added a new feature, it should have unit tests. If you've fixed a bug, it should
  *definitely* have unit tests.

* Your code should follow the `Python Style Guide`_ and/or match the surrounding code.

If you're new to Git or GitHub, take a look at the `GitHub help`_ site.

Please keep in mind however, that since the Warthog Client has a very specific purpose, pull
requests that are determined to be out of scope may not be merged.

Useful Commands
---------------

As you do development on the Warthog Client, the following commands might come in handy. Note
that all these commands assume you are in the context of the virtualenv you set up earlier.

Build the documentation.

.. code-block:: bash

    $ fab clean docs

Run the unit tests for Python 2.7, 3.3, and 3.4.

.. code-block:: bash

    $ tox test

Run the unit tests for a specific Python version.

.. code-block:: bash

    $ TOXENV=py27 tox test

Run the PyLint tool to find bugs or places where best practices are not being followed.

.. code-block:: bash

    $ fab lint

Check how much of the code in the Warthog client is covered by unit tests.

.. code-block:: bash

    $ fab coverage


.. _pip: https://pip.pypa.io/en/latest/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _Git: http://git-scm.com/
.. _fork: https://help.github.com/articles/fork-a-repo
.. _pull request: https://help.github.com/articles/be-social/#pull-requests
.. _GitHub help: https://help.github.com/
.. _squashing: http://blog.steveklabnik.com/posts/2012-11-08-how-to-squash-commits-in-a-github-pull-request
.. _rebasing: https://help.github.com/articles/using-git-rebase/
.. _Python Style Guide: https://www.python.org/dev/peps/pep-0008/
