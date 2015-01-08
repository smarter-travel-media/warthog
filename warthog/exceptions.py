# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2015 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions raised by the Warthog client or library.
"""


class WarthogError(Exception):
    """Base for all errors raised by the Warthog library."""

    def __init__(self, msg):
        super(WarthogError, self).__init__()
        self.msg = msg

    def __str__(self):
        return self.msg


class WarthogConfigError(WarthogError):
    """Base for errors raised while parsing or loading configuration."""


class WarthogNoConfigFileError(WarthogConfigError):
    """No configuration file could be found."""

    def __init__(self, msg, locations_checked=None):
        super(WarthogNoConfigFileError, self).__init__(msg)
        self.locations_checked = list(locations_checked) if locations_checked is not None else []

    def __str__(self):
        out = [self.msg]
        if self.locations_checked is not None:
            out.append('Locations checked: ' + ', '.join(self.locations_checked))
        return '. '.join(out)


class WarthogMalformedConfigFileError(WarthogConfigError):
    """The configuration file is missing required sections or fields."""

    def __init__(self, msg, missing_section=None, missing_option=None):
        super(WarthogMalformedConfigFileError, self).__init__(msg)
        self.missing_section = missing_section
        self.missing_option = missing_option

    def __str__(self):
        out = [self.msg]
        if self.missing_section is not None:
            out.append('Missing-section: {0}'.format(self.missing_section))
        if self.missing_option is not None:
            out.append('Missing-option: {0}'.format(self.missing_option))
        return '. '.join(out)


class WarthogApiError(WarthogError):
    """Base for errors raised in the course of interacting with the load balancer."""

    def __init__(self, msg, api_msg=None, api_code=None):
        super(WarthogApiError, self).__init__(msg)
        self.api_msg = api_msg
        self.api_code = api_code

    def __str__(self):
        out = [self.msg]
        if self.api_msg is not None:
            # Some error messages from the A10 end with a period, others don't
            out.append('API-message: {0}'.format(self.api_msg.rstrip('.')))
        if self.api_code is not None:
            out.append('API-code: {0}'.format(self.api_code))
        return '. '.join(out)


class WarthogAuthFailureError(WarthogApiError):
    """The credentials for authentication are invalid."""


class WarthogInvalidSessionError(WarthogApiError):
    """The session ID used while performing some action is unrecognized."""


class WarthogAuthCloseError(WarthogApiError):
    """There was some error while trying to end a session."""


class WarthogNodeError(WarthogApiError):
    """Base for errors specific to operating on some individual node."""

    def __init__(self, msg, api_msg=None, api_code=None, server=None):
        super(WarthogNodeError, self).__init__(msg, api_msg=api_msg, api_code=api_code)
        self.server = server


class WarthogNoSuchNodeError(WarthogNodeError):
    """The host being operated on is unrecognized."""


class WarthogNodeStatusError(WarthogNodeError):
    """There was some error while getting the status of a node."""


class WarthogNodeEnableError(WarthogNodeError):
    """There was some error while trying to enable a node."""


class WarthogNodeDisableError(WarthogNodeError):
    """There was some error while trying to disable a node."""
