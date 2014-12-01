# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions raised by the Warthog client or library.
"""


class WarthogError(Exception):
    """Base for all errors raised by the Warthog library.

    :ivar basestring msg: Descriptive error message for this error.
    """

    def __init__(self, msg):
        """Set the message for this exception."""
        super(WarthogError, self).__init__()
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return '{clazz}("{msg}")'.format(clazz=self.__class__.__name__, msg=self.msg)


class WarthogConfigError(WarthogError):
    """Base for errors raised while parsing or loading configuration."""


class WarthogNoConfigFileError(WarthogConfigError):
    """No configuration file could be found."""

    def __init__(self, msg, locations_checked=None):
        """Set the message for this exception and an optional list of paths
        that were checked for configuration files.
        """
        super(WarthogNoConfigFileError, self).__init__(msg)
        self.locations_checked = list(locations_checked) if locations_checked is not None else []

    def __str__(self):
        out = [self.msg]
        if self.locations_checked is not None:
            out.append('Locations checked: ' + ', '.join(self.locations_checked))
        return '. '.join(out)

    def __repr__(self):
        return '{clazz}("{msg}", locations_checked={locations_checked})'.format(
            self.msg, self.locations_checked)


class WarthogMalformedConfigFileError(WarthogConfigError):
    """The configuration file is missing required sections or fields."""

    def __init__(self, msg, missing_section=None, missing_option=None):
        """Set the message for this exception and optional missing sections
        or options expected in the configuration file.
        """
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

    def __repr__(self):
        return ('{clazz}("{msg}", missing_section="{missing_section}", '
                'missing_option="{missing_option}")').format(clazz=self.__class__.__name__,
                                                             msg=self.msg,
                                                             missing_section=self.missing_section,
                                                             missing_option=self.missing_option)


class WarthogApiError(WarthogError):
    """Base for errors raised in the course of interacting with the load balancer.

    :ivar basestring msg: Descriptive error message for this error.
    :ivar basestring api_msg: Error message for this particular problem from the
        load balancer API if available.
    :ivar int api_code: Error code for this particular problem from the load balancer
        API if available.
    """

    def __init__(self, msg, api_msg=None, api_code=None):
        """Set the message for this exception and optional message and code from
        the load balancer API.
        """
        super(WarthogApiError, self).__init__(msg)
        self.api_msg = api_msg
        self.api_code = api_code

    def __str__(self):
        out = [self.msg]
        if self.api_msg is not None:
            out.append('API-message: {0}'.format(self.api_msg))
        if self.api_code is not None:
            out.append('API-code: {0}'.format(self.api_code))
        return '. '.join(out)

    def __repr__(self):
        return '{clazz}("{msg}", api_msg="{api_msg}", api_code={api_code})'.format(
            clazz=self.__class__.__name__, msg=self.msg, api_msg=self.api_msg,
            api_code=self.api_code)


class WarthogAuthFailureError(WarthogApiError):
    """The credentials for authentication are invalid."""


class WarthogNoSuchNodeError(WarthogApiError):
    """The host being operated on is unrecognized."""


class WarthogInvalidSessionError(WarthogApiError):
    """The session ID used while performing some action is unrecognized."""


class WarthogNodeStatusError(WarthogApiError):
    """There was some error while getting the status of a node."""


class WarthogNodeEnableError(WarthogApiError):
    """There was some error while trying to enable a node."""


class WarthogNodeDisableError(WarthogApiError):
    """There was some error while trying to disable a node."""


class WarthogAuthCloseError(WarthogApiError):
    """There was some error while trying to end a session."""
