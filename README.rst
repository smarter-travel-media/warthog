Warthog
=======

.. image:: https://travis-ci.org/smarter-travel-media/warthog.png?branch=master
    :target: https://travis-ci.org/smarter-travel-media/warthog

**WARNING** - This is pre-alpha software and subject to breaking changes and/or bugs.

Warthog is a simple Python client for interacting with A10 load balancers. The target
use case is for safely removing servers from pools in a load balancer during a deployment.
It is available under the MIT license.

Features
--------
* Waiting for servers to finish all requests when being disabled
* Graceful handling of transient errors with optional retry logic
* Support for interacting with the load balancer API using SSL
* Python 2.6 -- 3.4
* Thread safety

Installation
------------

To install Warthog, simply run:

.. code-block:: bash

    $ pip install warthog

Usage
-----

Using the client is easy!

.. code-block:: python

    from warthog.api import WarthogClient

    client = WarthogClient('https://lb.example.com', 'user', 'password')

    client.disable_server('app1.example.com')
    # Install something on the server or restart your application
    client.enable_server('app1.example.com')

    # Or, use the client as a context manager!

    with client.disabled_context('app1.example.com'):
        # install something on the server or restart your application
        pass


See `the docs <https://warthog.readthedocs.org/>`_ for more information.

Code
----

The source code is available at https://github.com/smarter-travel-media/warthog

Documentation
-------------

Documentation is available at https://warthog.readthedocs.org/

Changes
-------

The change log is available at https://warthog.readthedocs.org/en/latest/changes.html
