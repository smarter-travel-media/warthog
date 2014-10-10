.. Warthog documentation master file, created by
   sphinx-quickstart on Mon Sep 29 13:06:53 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Warthog
=======

A simple Python client for A10 load balancers

**WARNING** - This is pre-alpha software and subject to breaking changes and/or bugs.

Warthog is a simple Python client for interacting with A10 load balancers. The target
use case is for safely removing servers from pools in a load balancer during a deployment.

Since the target use case is only aimed at deployments, Warthog supports far fewer types
of operations than something like the `official <https://github.com/a10networks/acos-client>`_
client.

Features
--------
* Waiting for servers to finish all requests when being disabled
* Graceful handling of transient errors with optional retry logic
* Support for interacting with the load balancer API using SSL
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

Contents
--------

.. toctree::
   :maxdepth: 2

   design
   usage
   api
   changes

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

