Install
=======

The sections below will go over how to install the Warthog client from the Python
Package Index (PyPI) or how to install it from source. Both ways to install the
client can be done globally on a machine or within the context of a virtualenv.

Prerequisites
-------------

These instructions assume that you have the following things available.

* Python 2.6 - 2.7 or Python 3.3 - Python 3.4
* The virtualenv_ tool
* The pip_ tool
* Git_

Requirements
------------

Warthog depends on the following libraries / projects. If you have Python installed
and use the pip_ tool for installation, these should be installed automatically.

* Python 2.6 - 2.7 or Python 3.3 - Python 3.4
* The Requests_ library (HTTP library), version 2.6 or higher
* The Click_ library (command line interface library), version 3.3 or higher

Install from PyPI
-----------------

If you're planning on installing from PyPI, the process is pretty easy. Depending
on how you want to use the client, you have a few options.

Globally
~~~~~~~~

You can install the client globally on a machine (using the system Python version)
and it will be available for all users of the machine. This will typically require
root or administrator permissions.

.. code-block:: bash

    $ pip install warthog


Virtual Environment
~~~~~~~~~~~~~~~~~~~

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

First you'll need to get the source code of the client using Git.

.. code-block:: bash

    $ git clone https://github.com/smarter-travel-media/warthog.git


Globally
~~~~~~~~

Like installation from PyPI, installation from source can be done globally for all users
of a machine. As above, this will typically require root or administrator permissions.

.. code-block:: bash

    $ cd warthog && pip install .

Virtual Environment
~~~~~~~~~~~~~~~~~~~

You can also install the client from source into a virtual environment.

.. code-block:: bash

    # Create your new virtual environment
    $ virtualenv my-warthog-install

    # Enter the virtual environment
    $ source my-warthog-install/bin/activate

    # Install the client from the source checkout we made above
    $ cd warthog && pip install .


.. _pip: https://pip.pypa.io/en/latest/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _Git: http://git-scm.com/
.. _Requests: http://docs.python-requests.org/en/latest/
.. _Click: http://click.pocoo.org/3/