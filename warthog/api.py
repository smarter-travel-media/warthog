# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.api
~~~~~~~~~~~

Publicly importable API for the Warthog client and library.
"""

from .core import (
    NodeActiveConnectionsCommand,
    NodeDisableCommand,
    NodeEnableCommand,
    NodeStatusCommand,
    SessionEndCommand,
    SessionStartCommand,
    STATUS_DISABLED,
    STATUS_DOWN,
    STATUS_ENABLED)

from .client import (
    CommandFactory,
    WarthogClient)

from .config import (
    WarthogConfigLoader,
    WarthogConfigSettings,
    DEFAULT_CONFIG_ENCODING,
    DEFAULT_CONFIG_LOCATIONS)

from .transport import get_transport_factory

from .exceptions import (
    WarthogError,
    WarthogAuthCloseError,
    WarthogAuthFailureError,
    WarthogInvalidSessionError,
    WarthogNodeDisableError,
    WarthogNodeEnableError,
    WarthogNodeStatusError,
    WarthogNoSuchNodeError
)


__all__ = [
    # warthog.core
    'NodeActiveConnectionsCommand',
    'NodeDisableCommand',
    'NodeEnableCommand',
    'NodeStatusCommand',
    'SessionEndCommand',
    'SessionStartCommand',
    'STATUS_DISABLED',
    'STATUS_DOWN',
    'STATUS_ENABLED',

    # warthog.client
    'CommandFactory',
    'WarthogClient',

    # warthog.config
    'WarthogConfigLoader',
    'WarthogConfigSettings',
    'DEFAULT_CONFIG_ENCODING',
    'DEFAULT_CONFIG_LOCATIONS',

    # warthog.transport
    'get_transport_factory',

    # warthog.exceptions
    'WarthogError',
    'WarthogAuthCloseError',
    'WarthogAuthFailureError',
    'WarthogInvalidSessionError',
    'WarthogNodeDisableError',
    'WarthogNodeEnableError',
    'WarthogNodeStatusError',
    'WarthogNoSuchNodeError'
]
