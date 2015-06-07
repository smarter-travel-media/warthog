Warthog
=======

.. image:: https://travis-ci.org/smarter-travel-media/warthog.png?branch=master
    :target: https://travis-ci.org/smarter-travel-media/warthog

**WARNING** - This is beta software and subject to breaking changes and/or bugs.

Warthog is a simple Python client for interacting with A10 load balancers. The target
use case is for safely removing servers from pools in a load balancer during a deployment.
It is available under the MIT license.

Features
--------
* Waiting for servers to finish all requests when being disabled
* Graceful handling of transient errors with optional retry logic
* Support for interacting with the load balancer API using SSL
* Works with Python 2.6, 2.7, 3.3, and 3.4+
* Thread safety

Installation
------------

To install Warthog, simply run:

.. code-block:: bash

    $ pip install warthog

Dependencies
------------
* `requests <https://github.com/kennethreitz/requests>`_ by Kenneth Reitz, version 2.6 or higher
* `click <https://github.com/mitsuhiko/click>`_ by Armin Ronacher, version 3.3 or higher

Usage
-----

Using the client is easy!

.. code-block:: python

    from warthog.api import WarthogClient

    def install_my_project(server):
        pass

    client = WarthogClient('https://lb.example.com', 'user', 'password')

    client.disable_server('app1.example.com')
    install_my_project('app1.example.com')
    client.enable_server('app1.example.com')


See `the docs <https://warthog.readthedocs.org/>`_ for more information.

Documentation
-------------

The latest documentation is available at https://warthog.readthedocs.org/en/latest/

Source
------

The source code is available at https://github.com/smarter-travel-media/warthog

Download
--------

Python packages are available at https://pypi.python.org/pypi/warthog

Changes
-------

The change log is available at https://warthog.readthedocs.org/en/latest/changes.html
