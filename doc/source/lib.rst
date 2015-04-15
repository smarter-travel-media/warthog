Library
=======

The public API of the Warthog library is maintained in the :mod:`warthog.api`
module. This is done for the purposes of clearly identifying which parts of
the library are public and which parts are internal.

Functionality in the :mod:`warthog.client`, :mod:`warthog.config`, :mod:`warthog.transport`,
and :mod:`warthog.exceptions` modules is included in this module under a single, flat
namespace. This allows a simple and consistent way to interact with the library.

.. note::

    When using the library, always make sure to access classes and functions through
    the :mod:`warthog.api` module, not each individual module.

.. automodule:: warthog.client
    :special-members: __init__,__call__,__enter__,__exit__
    :members: WarthogClient, CommandFactory
    :undoc-members:

.. automodule:: warthog.config
    :special-members: __init__,__call__,__enter__,__exit__
    :members: WarthogConfigLoader, WarthogConfigSettings
    :undoc-members:

.. automodule:: warthog.transport
    :special-members: __init__,__call__,__enter__,__exit__
    :members: get_transport_factory
    :undoc-members:

.. automodule:: warthog.exceptions
    :special-members: __init__
    :members:
    :undoc-members:
    :show-inheritance:
