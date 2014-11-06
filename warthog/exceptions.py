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
    """Base for all expected errors raised by the Warthog client and library.

    In this case, 'expected' means things that could conceivably happen in the
    normal course of interacting with the load balancer. Exceptions that aren't
    expected will not extend from this class and will usually indicate bugs in
    the library.

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
        super(WarthogError, self).__init__()
        self.msg = msg
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


class WarthogAuthFailureError(WarthogError):
    """The credentials for authentication are invalid."""


class WarthogNoSuchNodeError(WarthogError):
    """The host being operated on is unrecognized."""


class WarthogInvalidSessionError(WarthogError):
    """The session ID used while performing some action is unrecognized."""


class WarthogNodeStatusError(WarthogError):
    """There was some error while getting the status of a node."""


class WarthogNodeEnableError(WarthogError):
    """There was some error while trying to enable a node."""


class WarthogNodeDisableError(WarthogError):
    """There was some error while trying to disable a node."""


class WarthogAuthCloseError(WarthogError):
    """There was some error while trying to end a session."""
