API
===

The public API of the Warthog library is maintained in the :mod:`warthog.api`
module. This is done for the purposes of clearly identifying which parts of
the library are public and which parts are internal.

Functionality in the :mod:`warthog.core`, :mod:`warthog.client`, and
:mod:`warthog.transport` modules is included in this module under a single, flat
namespace. This allows a simple and consistent way to interact with the library.

Exceptions from the :mod:`warthog.exceptions` module are intentionally not
included in the :mod:`warthog.api` module. If you wish to handle exceptions
raised by the Warthog library, the :mod:`warthog.exceptions` module must be
imported separately.

.. automodule:: warthog.core
    :special-members: __init__,__call__,__enter__,__exit__
    :members: SessionStartCommand, SessionEndCommand, NodeActiveConnectionsCommand,
        NodeDisableCommand, NodeEnableCommand, NodeStatusCommand
    :undoc-members:
    :show-inheritance:

.. automodule:: warthog.client
    :special-members: __init__,__call__,__enter__,__exit__
    :members: CommandFactory, WarthogClient
    :undoc-members:
    :show-inheritance:

.. automodule:: warthog.transport
    :special-members: __init__,__call__,__enter__,__exit__
    :members: get_transport_factory
    :undoc-members:
    :show-inheritance:

.. automodule:: warthog.exceptions
    :special-members: __init__
    :members:
    :undoc-members:
    :show-inheritance:
