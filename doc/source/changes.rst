Change Log
==========

0.4.2 - 2014-10-29
------------------
* Documentation improvements (:doc:`dev`).
* Test coverage improvements in :mod:`warthog.cli`.

0.4.1 - 2014-10-23
------------------
* Add CLI tool for using the Warthog Client. See :doc:`cli`.
* Add :meth:`warthog.client.WarthogClient.get_connections` method for getting the
  number of active connections to a server.
* Add Exceptions in :mod:`warthog.exceptions` to the public api in :mod:`warthog.api`.
* Add config parsing module :mod:`warthog.config` and add it to the public api in :mod:`warthog.api`.

0.3.1 - 2014-10-17
------------------
* Change ``setup.py`` script to not require setuptools.

0.3.0 - 2014-10-16
------------------
* Add :doc:`install` documentation.
* Change authentication request (:class:`warthog.core.SessionStartCommand`) to use ``POST``
  instead of ``GET`` though there doesn't seem to be any actual difference as far as the
  load balancer API is concerned.

0.2.0 - 2014-10-14
------------------
* Add :doc:`design`, :doc:`usage`, and :doc:`lib` documentation.
* Add test to ensure exported API is consistent.

0.1.0 - 2014-10-11
------------------
* Initial release
