.. Warthog documentation master file, created by
   sphinx-quickstart on Mon Sep 29 13:06:53 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. NOTE: Make sure this page is kept up to date with README.rst

.. figure:: _static/logo.png
    :align: center

Warthog
=======

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
* `requests <https://github.com/kennethreitz/requests>`_  by Kenneth Reitz
* `click <https://github.com/mitsuhiko/click>`_ by Armin Ronacher

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


Contents
--------

.. toctree::
   :maxdepth: 2

   install
   design
   usage
   lib
   cli
   dev
   release
   changes

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
