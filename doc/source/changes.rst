Changelog
=========

0.10.0 - Future release
-----------------------
* Add option to :class:`warthog.client.WarthogClient` to allow alternate SSL or TLS versions
  to be used easily. Fixes `#6 <https://github.com/smarter-travel-media/warthog/issues/6>`_.
* **Breaking change** - Passing a ``None`` value to :func:`warthog.transport.get_transport_factory`
  for the ``ssl_version`` parameter will now use the Warthog library default (TLSv1) instead of
  letting requests/urllib3 pick the default.
* Add support for specifying an optional ``ssl_version`` parameter in INI configuration files.
  Fixes `#4 <https://github.com/smarter-travel-media/warthog/issues/4>`_.
* Change ``verify`` to be optional in INI configuration files.

0.9.1 - 2015-08-07
------------------
* Fix bug where a config file needed to be specified by the CLI client even when
  not required (such as when displaying help). Fixes
  `#3 <https://github.com/smarter-travel-media/warthog/issues/3>`_.

0.9.0 - 2015-06-04
------------------
* Replace examples documentation with more in depth usage guide (:doc:`usage`).
* Add documentation for performing a release of the library (:doc:`release`).
* Move enabling/disabling certificate verification to the :class:`warthog.client.WarthogClient`
  class so that using self-signed certificates is less of a hassle and requires
  less code.

0.8.3 - 2015-03-18
------------------
* Dependency on `requests <https://github.com/kennethreitz/requests>`_ updated to version 2.6.0.
* Packaging fixes (use ``twine`` for uploads to PyPI, stop using the setup.py ``register`` command).
* Minor documentation updates.

0.8.2 - 2015-02-09
------------------
* Small documentation fixes.
* Add project logo to documentation.
* Dependency on `requests <https://github.com/kennethreitz/requests>`_ updated to version 2.5.1.

0.8.1 - 2014-12-22
------------------
* Fixed small documentation issues and changed change log dates.

0.8.0 - 2014-12-22
------------------
* **Breaking change** - Changed errors raised by :class:`warthog.config.WarthogConfigLoader`
  to be subclasses of :class:`warthog.exceptions.WarthogConfigError` instead of using errors
  from the standard library (:class:`ValueError`, :class:`IOError`, :class:`RuntimeError`).
* **Breaking change** - Removed the ``warthog.client.WarthogClient.disabled_context`` context
  manager method since the level of abstraction didn't match the rest of the methods in the
  client.
* **Breaking change** - Removed all command classes in :mod:`warthog.core` from the public API
  (``warthog.api``). Users wishing to use them may do so at their own risk.
* Change all server-specific exceptions to be based on :class:`warthog.exceptions.WarthogNodeError`.
* Improve error handling for CLI client when the configuration file contains an invalid load
  balancer host (or port, etc.).
* Bundled 3rd-party libs moved to the :mod:`warthog.packages` package.
* Dependency on `requests <https://github.com/kennethreitz/requests>`_ updated to version 2.5.0.

0.7.0 - 2014-11-24
------------------
* **Breaking change** - Changed error hierarchy so that all errors related to interacting
  with the load balancer now extend from :class:`warthog.exceptions.WarthogApiError`. The
  root error class :class:`warthog.exceptions.WarthogError` no longer contains any
  functionality specific to making API requests to the load balancer.

0.6.0 - 2014-11-20
------------------
* **Breaking change** - Removed :meth:`warthog.config.WarthogConfigLoader.parse_configuration`
  method and split the functionality into two new methods. Additionally, the class is
  now thread safe.
* Renamed "Usage" documentation section to "Examples".

0.5.0 - 2014-11-03
------------------
* **Breaking change** - Changed all command ``.send()`` methods in :mod:`warthog.core`
  to not take any arguments to given them a consistent interface.
* Examples documentation improvements.
* Various code quality improvements.

0.4.2 - 2014-10-29
------------------
* Documentation improvements (:doc:`dev`).
* Test coverage improvements in :mod:`warthog.cli`.

0.4.1 - 2014-10-23
------------------
* Added CLI tool for using the Warthog Client. See :doc:`cli`.
* Added :meth:`warthog.client.WarthogClient.get_connections` method for getting the
  number of active connections to a server.
* Added Exceptions in :mod:`warthog.exceptions` to the public api in :mod:`warthog.api`.
* Added config parsing module :mod:`warthog.config` and add it to the public api in :mod:`warthog.api`.

0.3.1 - 2014-10-17
------------------
* Changed ``setup.py`` script to not require setuptools.

0.3.0 - 2014-10-16
------------------
* Added :doc:`install` documentation.
* Changed authentication request (:class:`warthog.core.SessionStartCommand`) to use ``POST``
  instead of ``GET`` though there doesn't seem to be any actual difference as far as the
  load balancer API is concerned.

0.2.0 - 2014-10-14
------------------
* Added :doc:`design`, Examples, and :doc:`lib` documentation.
* Added test to ensure exported API is consistent.

0.1.0 - 2014-10-11
------------------
* Initial release
