# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2015 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.core
~~~~~~~~~~~~

Basic building blocks for authentication and interaction with a load balancer.
"""

import logging

import warthog.exceptions
# pylint: disable=import-error,no-name-in-module
from .packages.six.moves import urllib


STATUS_ENABLED = 'enabled'

STATUS_DISABLED = 'disabled'

STATUS_DOWN = 'down'

ERROR_CODE_GRACEFUL_SHUTDOWN = 67174416

ERROR_CODE_INVALID_SESSION = 1009

ERROR_CODE_NO_SUCH_SERVER = 67174402

TRANSIENT_ERRORS = frozenset([
    ERROR_CODE_GRACEFUL_SHUTDOWN
])

_API_VERSION = 'v2'

_ACTION_AUTHENTICATE = 'authenticate'

_ACTION_ENABLE = _ACTION_DISABLE = 'slb.server.update'

_ACTION_STATUS = _ACTION_STATISTICS = 'slb.server.fetchStatistics'

_ACTION_CLOSE_SESSION = 'session.close'


def get_log():
    """Get the :class:`logging.Logger` instance used by the Warthog library.

    :return: Logger for the entire library
    :rtype: logging.Logger
    """
    return logging.getLogger('warthog')


class _ErrorHandlerMixin(object):
    """Mixin class for translating error responses to WarthogApiError instances."""

    def _extract_error(self, default_cls, message, response):
        """Return a WarthogApiError instance with the given error message appropriate
        to the given API response, falling back to an instance of the default class.

        If the default class is a node-specific error, the name of the current node
        will be provided with the ``server`` keyword argument.

        The ``default_cls`` must be a subclass of ``WarthogApiError``.
        """
        server = getattr(self, '_server', None)
        msg, code = _extract_error_message(response)

        if code == ERROR_CODE_INVALID_SESSION:
            return warthog.exceptions.WarthogInvalidSessionError(
                message, api_msg=msg, api_code=code)
        if code == ERROR_CODE_NO_SUCH_SERVER:
            return warthog.exceptions.WarthogNoSuchNodeError(
                message, api_msg=msg, api_code=code, server=server)
        # If this is a node specific error type include the value of the '_server'
        # attribute of the class that this is being invoked from as a keyword arg.
        if issubclass(default_cls, warthog.exceptions.WarthogNodeError):
            return default_cls(message, api_msg=msg, api_code=code, server=server)
        return default_cls(message, api_msg=msg, api_code=code)


class SessionStartCommand(_ErrorHandlerMixin):
    """Command to authenticate with the load balancer and start a new session
    to be used by subsequent commands.

    This class is thread safe.
    """
    _logger = get_log()

    def __init__(self, transport, scheme_host, username, password):
        """Set the transport layer and necessary credentials to authenticate with
        the load balancer.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring username: Name of the user to authenticate with.
        :param basestring password: Password for the user to authenticate with.
        """
        self._transport = transport
        self._scheme_host = scheme_host
        self._username = username
        self._password = password

    def send(self):
        """Make an authentication request and return the session token that should
        be included in all subsequent requests to the load balancer.

        :return: The session token that should be used for all subsequent requests
            made to the load balancer.
        :rtype: unicode
        :raises warthog.exceptions.WarthogAuthFailureError: If the authentication
            failed for some reason. The exception will contain an error message and
            error code that provides more detail about the failure. Common reasons
            for this error include using invalid username or password.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_AUTHENTICATE)
        params['username'] = self._username
        params['password'] = self._password

        self._logger.debug('Making session start POST request to %s', url)
        response = self._transport.post(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if 'session_id' not in json:
            raise self._extract_error(
                warthog.exceptions.WarthogAuthFailureError,
                'Authentication failure with {0}'.format(self._scheme_host),
                json['response'])

        return json['session_id']


class _AuthenticatedCommand(object):
    """Base class for making requests to the load balancer using an existing session
    ID from a previous :class:`SessionStartCommand` request.

    :ivar requests.Session _transport:
    :ivar basestring _scheme_host:
    :ivar basestring _session_id:
    """
    _logger = get_log()

    def __init__(self, transport, scheme_host, session_id):
        """Set the requests transport layer, scheme and host of the load balancer,
        and existing session ID to use for authentication.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring session_id: Session ID from a previous authentication request
            made to the load balancer.
        """
        self._transport = transport
        self._scheme_host = scheme_host
        self._session_id = session_id

    def send(self):
        """Abstract method for making a request to the load balancer API and parsing
        the result and returning any meaningful information (implementation specific).
        """
        raise NotImplementedError()


class SessionEndCommand(_AuthenticatedCommand, _ErrorHandlerMixin):
    """Command for ending a previously authenticated session with the load balancer.

    This class is thread safe.
    """

    def send(self):
        """Close an existing session and return ``True`` if closing it was successful.

        :return: True if the current session could be closed
        :rtype: bool
        :raises warthog.exceptions.WarthogInvalidSessionError: If the load balancer
            did not recognize the session this command is being run as part of.
        :raises warthog.exceptions.WarthogAuthCloseError: If the session could not be
            closed. This is usually the result of the session ID being invalid or the
            session already being closed before this command is run.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_CLOSE_SESSION, self._session_id)

        self._logger.debug('Making session close POST request to %s', url)
        response = self._transport.post(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if json['response']['status'] == 'fail':
            raise self._extract_error(
                warthog.exceptions.WarthogAuthCloseError,
                'Could not close session {0} on {1}'.format(
                    self._session_id, self._scheme_host),
                json['response'])

        return json['response']['status'] == 'OK'


class NodeEnableCommand(_AuthenticatedCommand, _ErrorHandlerMixin):
    """Command to mark a particular server as enabled.

    This class is thread safe.
    """

    def __init__(self, transport, scheme_host, session_id, server):
        """Set the requests transport layer, scheme and host of the load balancer,
        existing session ID to use for authentication, and hostname of the server
        to enable.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring session_id: Session ID from a previous authentication request
            made to the load balancer.
        :param basestring server: Host name of the server to enable.
        """
        super(NodeEnableCommand, self).__init__(transport, scheme_host, session_id)
        self._server = server

    def send(self):
        """Mark a server as 'enabled' at the node level and return ``True`` if it was
        successfully enabled.

        :return: True if the server was marked as enabled
        :rtype: bool
        :raises warthog.exceptions.WarthogInvalidSessionError: If the load balancer
            did not recognize the session this command is being run as part of.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the server was not
            recognized by the load balancer.
        :raises warthog.exceptions.WarthogNodeEnableError: If the server could
            not be enabled for any other reason.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_ENABLE, self._session_id)
        params['name'] = self._server
        params['server'] = self._server
        params['status'] = 1

        self._logger.debug('Making node enable POST request for %s', self._server)
        response = self._transport.post(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if json['response']['status'] == 'fail':
            raise self._extract_error(
                warthog.exceptions.WarthogNodeEnableError,
                'Could not enable node {0}'.format(self._server),
                json['response'])

        return json['response']['status'] == 'OK'


class NodeDisableCommand(_AuthenticatedCommand, _ErrorHandlerMixin):
    """Command to mark a particular server as disabled.

    This class is thread safe.
    """

    def __init__(self, transport, scheme_host, session_id, server):
        """Set the requests transport layer, scheme and host of the load balancer,
        existing session ID to use for authentication, and hostname of the server
        to disable.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring session_id: Session ID from a previous authentication request
            made to the load balancer.
        :param basestring server: Host name of the server to disable.
        """
        super(NodeDisableCommand, self).__init__(transport, scheme_host, session_id)
        self._server = server

    def send(self):
        """Mark a server as 'disabled' at the node level and return ``True`` if it
        was successfully disabled.

        :return: True if the server was marked as disabled
        :rtype: bool
        :raises warthog.exceptions.WarthogInvalidSessionError: If the load balancer
            did not recognize the session this command is being run as part of.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the server was not
            recognized by the load balancer.
        :raises warthog.exceptions.WarthogNodeDisableError: If the server could
            not be disabled for any other reason.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_ENABLE, self._session_id)
        params['name'] = self._server
        params['server'] = self._server
        params['status'] = 0

        self._logger.debug('Making node disable POST request for %s', self._server)
        response = self._transport.post(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if json['response']['status'] == 'fail':
            raise self._extract_error(
                warthog.exceptions.WarthogNodeDisableError,
                'Could not disable node {0}'.format(self._server),
                json['response'])

        return json['response']['status'] == 'OK'


class NodeStatusCommand(_AuthenticatedCommand, _ErrorHandlerMixin):
    """Command to get the current status ('enabled', 'disabled', 'down') of a particular
    server.

    This class is thread safe.
    """

    def __init__(self, transport, scheme_host, session_id, server):
        """Set the requests transport layer, scheme and host of the load balancer,
        existing session ID to use for authentication, and hostname of the server
        to get the status of.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring session_id: Session ID from a previous authentication request
            made to the load balancer.
        :param basestring server: Host name of the server to get the status of.
        """
        super(NodeStatusCommand, self).__init__(transport, scheme_host, session_id)
        self._server = server

    def send(self):
        """Get the current status of a server at the node level and return one of the
        ``STATUS_ENABLED``, ``STATUS_DISABLED``, ``STATUS_DOWN`` constants.

        :return: The status of the server as a constant string
        :rtype: basestring
        :raises warthog.exceptions.WarthogInvalidSessionError: If the load balancer
            did not recognize the session this command is being run as part of.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the server was not
            recognized by the load balancer.
        :raises warthog.exceptions.WarthogNodeStatusError: If the status of the server
            could not be determined for any other reason.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_STATUS, self._session_id)
        params['name'] = self._server

        self._logger.debug('Making node status GET request for %s', self._server)
        response = self._transport.get(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if 'server_stat' not in json:
            raise self._extract_error(
                warthog.exceptions.WarthogNodeStatusError,
                'Could not get status of {0}'.format(self._server),
                json['response'])

        status = json['server_stat']['status']
        if status == 0:
            return STATUS_DISABLED
        if status == 1:
            return STATUS_ENABLED
        if status == 2:
            return STATUS_DOWN

        raise warthog.exceptions.WarthogNodeStatusError(
            'Unknown status of {0}: status={1}'.format(self._server, status))


class NodeActiveConnectionsCommand(_AuthenticatedCommand, _ErrorHandlerMixin):
    """Command to get the number of active connections to a particular server.

    This class is thread safe.
    """

    def __init__(self, transport, scheme_host, session_id, server):
        """Set the requests transport layer, scheme and host of the load balancer,
        existing session ID to use for authentication, and hostname of the server
        to get active connections for.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring session_id: Session ID from a previous authentication request
            made to the load balancer.
        :param basestring server: Host name of the server to get active connections for.
        """
        super(NodeActiveConnectionsCommand, self).__init__(transport, scheme_host, session_id)
        self._server = server

    def send(self):
        """Get the current number of active connections for a node as an int.

        :return: The number of active connections for a node across all ports
        :rtype: int
        :raises warthog.exceptions.WarthogInvalidSessionError: If the load balancer
            did not recognize the session this command is being run as part of.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the server was not
            recognized by the load balancer.
        :raises warthog.exceptions.WarthogNodeStatusError: If the number of active
            connections to the server could not be determined for any other reason.
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_STATISTICS, self._session_id)
        params['name'] = self._server

        self._logger.debug('Making active connection count GET request for %s', self._server)
        response = self._transport.get(url, params=params)
        self._logger.debug(response.text)
        json = response.json()

        if 'server_stat' not in json:
            raise self._extract_error(
                warthog.exceptions.WarthogNodeStatusError,
                'Could not get status of {0}'.format(self._server),
                json['response'])

        return json['server_stat']['cur_conns']


def _extract_error_message(response):
    """Get a two element tuple of the form ``msg, code`` where ``msg`` is an
    error message returned by the API and ``code`` is a numeric code associated
    with that particular error.
    """
    if response['status'] == 'fail':
        return response['err']['msg'].strip(), response['err']['code']
    raise ValueError(
        "Unexpected response format from request: {0}".format(response))


def _get_base_url(scheme_host):
    """Get a URL to API of the load balancer, not including any query string
    parameters.
    """
    return urllib.parse.urljoin(
        scheme_host, 'services/rest/{version}/'.format(version=_API_VERSION))


def _get_base_query_params(action, session_id=None):
    """Get a dictionary of query string parameters to pass to the load balancer
    API based on the given action and optional session ID.
    """
    params = {
        'format': 'json',
        'method': action
    }

    if session_id is not None:
        params['session_id'] = session_id
    return params
