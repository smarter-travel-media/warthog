Install
=======

The sections below will go over how to install the Warthog client from the Python
Package Index (PyPI) (such as when using it in production) and how to install it
from source (such as when you are developing it).

Prerequisites
-------------

These instructions assume that you have the following things available.

* Python 2.6 - 2.7 or Python 3.3 - Python 3.4
* The virtualenv tool
* Git

Install from PyPI
-----------------

If you're planning on installing from PyPI, the process is pretty easy. Depending
on how you want to use the client, you have a few options.

You can install the client globally on a machine (using the system Python version)
and it will be available for all users of the machine. This will typically require
root or administrator permissions.

.. code-block:: bash

    $ pip install warthog


You can also install the client into a virtual environment. A virtual environment is
a self-contained Python installation into which you can install whatever you'd like
without root or administrator permissions. Packages installed in this environment will
only be available in the context of that environment.

.. code-block:: bash

    # Create your new virtual environment
    $ virtualenv my-warthog-install

    # Enter the virtual environment
    $ source my-warthog-install/bin/activate

    # Install the Warthog client
    $ pip install warthog


Install from Source
-------------------

If you're planning on making changes to the Warthog client, first you'll need to get
the source code of the client using Git.

.. code-block:: bash

    $ git clone https://github.com/smarter-travel-media/warthog.git


Next, we'll set up a virtual environment that we can install the client into along with
any dependencies need for development.

.. code-block:: bash

    $ cd warthog

    # Create the virtual environment
    $ virtualenv env

    # Enter the virtual environment
    $ source env/bin/activate

    # Install development and runtime dependencies
    $ pip install --requirement requirements-dev.txt --requirement requirements.txt

    # Next, install the Warthog client in 'editable' mode
    $ pip install --editable .

That's it. You should now be able to use the client from within the virtual environment
you set up.
