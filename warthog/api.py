# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2015 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.api
~~~~~~~~~~~

Publicly importable API for the Warthog client and library.
"""

from .core import (
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
    WarthogApiError,
    WarthogAuthCloseError,
    WarthogAuthFailureError,
    WarthogInvalidSessionError,
    WarthogNodeError,
    WarthogNodeDisableError,
    WarthogNodeEnableError,
    WarthogNodeStatusError,
    WarthogNoSuchNodeError,
    WarthogConfigError,
    WarthogMalformedConfigFileError,
    WarthogNoConfigFileError)


__all__ = [
    # warthog.core
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
    'WarthogApiError',
    'WarthogAuthCloseError',
    'WarthogAuthFailureError',
    'WarthogInvalidSessionError',
    'WarthogNodeError',
    'WarthogNodeDisableError',
    'WarthogNodeEnableError',
    'WarthogNodeStatusError',
    'WarthogNoSuchNodeError',
    'WarthogConfigError',
    'WarthogMalformedConfigFileError',
    'WarthogNoConfigFileError'
]
