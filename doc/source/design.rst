Design
======

Some of the principals, design decisions, and limitations of the Warthog library are
outlined below.

Purpose
-------

The target use case of the Warthog client is safely disabling servers while each server is
restarted or deployed to. Because of this, Warthog has a very slim feature set. The client
only exposes a small subset of operations available through the HTTP API for A10 load
balancers.

Node Level vs Group Level
-------------------------

When interacting with a server in a load balancer, there are typically two ways the server
can be manipulated -- at the node level and at the group level. Interacting with a server
at the node level means that it will disabled for all groups that the server belongs to.
Interacting with a server at the group level means that the server may be active for one
group and disabled for others.

The Warthog library embraces the idea that nodes should be single purpose and not run
multiple unrelated services. Because of this, Warthog supports interacting with servers
only at the node level, not the group level. When the status of servers is queried, when
servers are disabled, and when servers are enabled, all operations are at the node level.

Thread Safety
-------------

The main interfaces of the Warthog library (:class:`warthog.client.WarthogClient`,
:class:`warthog.client.CommandFactory`, and assorted classes in :mod:`warthog.config`) are
thread safe. Each class will also include a comment in the doc string that indicates if
it is thread safe. The Warthog library makes use of Requests_ (for making HTTP and HTTPS
calls to the load balancer API) which is also thread safe.

.. _Requests: http://docs.python-requests.org/en/latest/

SSL
---

The Warthog library supports interacting with a load balancer over HTTPS. By default
when using SSL, certificates will be verified_, and TSLv1 will be explicitly used. If
you wish to override either of these, you can do so when using the
:class:`warthog.client.WarthogClient` or in your configuration file.

.. _verified: http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification

Versions
--------

The Warthog library uses `semantic versioning`_ of the form ``major.minor.patch``. All
backwards incompatible changes after version ``1.0.0`` will increment the major version
number. All backwards incompatible changes prior to version ``1.0.0`` will increment the
minor version number.

Since this is a Python project, only the subset of the semantic versioning spec that is
compatible with `PEP-440`_ will be used.

Compatible and incompatible changes are defined in terms of use of the Python module
``warthog.api`` and use of the CLI program ``warthog``. Meaning, code that makes use
of the 1.0.0 version of ``warthog.api`` should not require any changes to make use of
the 1.1.0 version of ``warthog.api``.

.. _semantic versioning: http://semver.org/
.. _PEP-440: https://www.python.org/dev/peps/pep-0440/

Alternatives
------------

If your use case doesn't fit the design or goals of the Warthog client, don't despair,
you have options!

The official_ client supports many more operations, though, at the price of a reduced
level of abstraction.

You can also write_ your own client based on available documentation.

.. _official: https://github.com/a10networks/acos-client
.. _write: http://www.a10networks.com/products/axseries-aXAPI.php
