# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2016 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.core
~~~~~~~~~~~~

Basic building blocks for authentication and interaction with a load balancer.
"""

import logging

import requests

import warthog.exceptions
# pylint: disable=import-error,no-name-in-module
from .packages.six.moves import urllib

STATUS_ENABLED = 'enabled'

STATUS_DISABLED = 'disabled'

STATUS_DOWN = 'down'

ERROR_CODE_NO_SUCH_SERVER = 1023460352

ERROR_CODE_BAD_PERMISSION = 419545856

_PATH_AUTH = '/axapi/v3/auth'

_PATH_LOGOFF = '/axapi/v3/logoff'

_PATH_ENABLE = _PATH_DISABLE = '/axapi/v3/slb/server/{server}'

_PATH_STATUS = '/axapi/v3/slb/server/{server}/oper'

_PATH_CONNS = '/axapi/v3/slb/server/{server}/stats'


def get_log():
    """Get the :class:`logging.Logger` instance used by the Warthog library.

    :return: Logger for the entire library
    :rtype: logging.Logger
    """
    return logging.getLogger('warthog')


# pylint: disable=invalid-name,missing-docstring
def _extract_auth_error_from_payload(payload):
    err = payload['authorizationschema']['error'].strip()
    code = payload['authorizationschema']['code']
    return err, code


# pylint: disable=invalid-name,missing-docstring
def _extract_other_error_from_payload(payload):
    err = payload['response']['err']['msg'].strip()
    code = payload['response']['err']['code']
    return err, code


class _AuthErrorHandler(object):
    def __init__(self, host, user):
        self._host = host
        self._user = user

    # pylint: disable=no-self-use
    def can_handle(self, response):
        # pylint: disable=no-member
        return response.status_code == requests.codes.forbidden

    def handle(self, response):
        payload = response.json()
        err, code = _extract_auth_error_from_payload(payload)

        raise warthog.exceptions.WarthogAuthFailureError(
            'Authentication failure using user "{0}" with {1}'.format(self._user, self._host),
            api_msg=err, api_code=code
        )


class _SessionErrorHandler(object):
    def __init__(self, token):
        self._token = token

    # pylint: disable=no-self-use
    def can_handle(self, response):
        # pylint: disable=no-member
        return response.status_code == requests.codes.unauthorized

    def handle(self, response):
        payload = response.json()
        err, code = _extract_auth_error_from_payload(payload)

        raise warthog.exceptions.WarthogInvalidSessionError(
            'Invalid session or token "{0}"'.format(self._token),
            api_msg=err, api_code=code
        )


class _PermissionErrorHandler(object):
    def __init__(self, server):
        self._server = server

    # pylint: disable=no-self-use
    def can_handle(self, response):
        # pylint: disable=no-member
        if response.status_code != requests.codes.bad_request:
            return False

        payload = response.json()
        _, code = _extract_other_error_from_payload(payload)
        return code == ERROR_CODE_BAD_PERMISSION

    def handle(self, response):
        payload = response.json()
        err, code = _extract_other_error_from_payload(payload)

        raise warthog.exceptions.WarthogPermissionError(
            'Insufficient permissions to complete operation on {0}'.format(self._server),
            api_msg=err, api_code=code, server=self._server
        )


class _NoSuchServerErrorHandler(object):
    def __init__(self, server):
        self._server = server

    # pylint: disable=no-self-use
    def can_handle(self, response):
        # pylint: disable=no-member
        if response.status_code != requests.codes.not_found:
            return False

        payload = response.json()
        _, code = _extract_other_error_from_payload(payload)
        return code == ERROR_CODE_NO_SUCH_SERVER

    def handle(self, response):
        payload = response.json()
        err, code = _extract_other_error_from_payload(payload)

        raise warthog.exceptions.WarthogNoSuchNodeError(
            'No such node {0}'.format(self._server),
            api_msg=err, api_code=code, server=self._server
        )


class _OtherErrorHandler(object):
    # pylint: disable=no-self-use
    def can_handle(self, response):
        return not response.ok

    # pylint: disable=no-self-use
    def handle(self, response):
        payload = response.json()
        err, code = _extract_other_error_from_payload(payload)

        raise warthog.exceptions.WarthogApiError(
            'Unexpected API error, HTTP code {0}'.format(response.status_code),
            api_msg=err, api_code=code
        )


class _SuccessHandler(object):
    # pylint: disable=no-self-use
    def can_handle(self, _):
        return True

    # pylint: disable=no-self-use
    def handle(self, response):
        return response.json()


class _ResponseHandlerMixin(object):
    """Mixin class for translating error responses to WarthogApiError instances."""

    def _extract_payload(self, response):
        server = getattr(self, '_server', None)
        host = getattr(self, '_scheme_host', None)
        user = getattr(self, '_username', None)
        auth = getattr(self, '_auth_token', None)

        handlers = [
            _AuthErrorHandler(host, user),
            _SessionErrorHandler(auth),
            _NoSuchServerErrorHandler(server),
            _PermissionErrorHandler(server),
            _OtherErrorHandler(),
            _SuccessHandler()
        ]

        for handler in handlers:
            if handler.can_handle(response):
                return handler.handle(response)

        raise RuntimeError(
            "At least one configured handler should be able to handle the "
            "response (code {code}) but none did. This most likely indicates "
            "a bug in the Warthog library. Response {response}".format(
                code=response.status_code, response=response.text
            )
        )


def _get_endpoint_url(scheme_host, path):
    return urllib.parse.urljoin(scheme_host, path)


class SessionStartCommand(_ResponseHandlerMixin):
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
        url = _get_endpoint_url(self._scheme_host, _PATH_AUTH)
        params = {
            'credentials': {
                'username': self._username,
                'password': self._password
            }
        }

        self._logger.debug('Making session start POST request to %s', url)
        response = self._transport.post(url, json=params)
        self._logger.debug(response.text)

        payload = self._extract_payload(response)
        return payload['authresponse']['signature']


class _AuthenticatedCommand(object):
    """Base class for making requests to the load balancer using an existing session
    ID from a previous :class:`SessionStartCommand` request.

    :ivar requests.Session _transport:
    :ivar basestring _scheme_host:
    :ivar basestring _session_id:
    """
    _logger = get_log()

    def __init__(self, transport, scheme_host, auth_token):
        """Set the requests transport layer, scheme and host of the load balancer,
        and existing session ID to use for authentication.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring auth_token: Auth token from a previous authentication request
            made to the load balancer.
        """
        self._transport = transport
        self._scheme_host = scheme_host
        self._auth_token = auth_token

    def _auth_header(self):
        return {'Authorization': 'A10 {auth}'.format(auth=self._auth_token)}

    def send(self):
        """Abstract method for making a request to the load balancer API and parsing
        the result and returning any meaningful information (implementation specific).
        """
        raise NotImplementedError()


class SessionEndCommand(_AuthenticatedCommand, _ResponseHandlerMixin):
    """Command for ending a previously authenticated session with the load balancer.

    This class is thread safe.
    """

    def send(self):
        """Close an existing session and return ``True`` if closing it was successful.

        :return: True if the current session could be closed
        :rtype: bool
        :raises warthog.exceptions.WarthogApiError: If the session could not be
            closed. This is usually the result of the session ID being invalid or the
            session already being closed before this command is run.
        """
        url = _get_endpoint_url(self._scheme_host, _PATH_LOGOFF)

        self._logger.debug('Making session close POST request to %s', url)
        response = self._transport.post(url, headers=self._auth_header())
        self._logger.debug(response.text)
        payload = self._extract_payload(response)

        return payload['response']['status'] == 'OK'


class NodeEnableCommand(_AuthenticatedCommand, _ResponseHandlerMixin):
    """Command to mark a particular server as enabled.

    This class is thread safe.
    """

    def __init__(self, transport, scheme_host, auth_token, server):
        """Set the requests transport layer, scheme and host of the load balancer,
        existing session ID to use for authentication, and hostname of the server
        to enable.

        :param requests.Session transport: Configured requests session instance to
            use for making HTTP or HTTPS requests to the load balancer API.
        :param basestring scheme_host: Scheme and hostname of the load balancer to use for
            making API requests. E.g. 'https://lb.example.com' or 'http://10.1.2.3'.
        :param basestring auth_token: Session ID from a previous authentication request
            made to the load balancer.
        :param basestring server: Host name of the server to enable.
        """
        super(NodeEnableCommand, self).__init__(transport, scheme_host, auth_token)
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
        :raises warthog.exceptions.WarthogPermissionError: If the user doesn't
            have the required permissions to enable the server.
        :raises warthog.exceptions.WarthogApiError: If the server could not be
            enabled for any other reason.
        """
        url = _get_endpoint_url(self._scheme_host, _PATH_ENABLE)
        url = url.format(server=self._server)
        params = {'server': {'action': 'enable'}}

        self._logger.debug('Making node enable POST request for %s', self._server)
        response = self._transport.post(url, headers=self._auth_header(), json=params)
        self._logger.debug(response.text)
        payload = self._extract_payload(response)

        return payload['server']['action'] == 'enable'


class NodeDisableCommand(_AuthenticatedCommand, _ResponseHandlerMixin):
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
        :raises warthog.exceptions.WarthogPermissionError: If the user doesn't
            have the required permissions to disable the server.
        :raises warthog.exceptions.WarthogApiError: If the server could not be
            disabled for any other reason.
        """
        url = _get_endpoint_url(self._scheme_host, _PATH_DISABLE)
        url = url.format(server=self._server)
        params = {'server': {'action': 'disable'}}

        self._logger.debug('Making node disable POST request for %s', self._server)
        response = self._transport.post(url, headers=self._auth_header(), json=params)
        self._logger.debug(response.text)
        payload = self._extract_payload(response)

        return payload['server']['action'] == 'disable'


class NodeStatusCommand(_AuthenticatedCommand, _ResponseHandlerMixin):
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
            was not a recognized status.
        :raises warthog.exceptions.WarthogApiError: If there are any other problems
            getting the status of the server.
        """
        url = _get_endpoint_url(self._scheme_host, _PATH_STATUS)
        url = url.format(server=self._server)

        self._logger.debug('Making node status GET request for %s', self._server)
        response = self._transport.get(url, headers=self._auth_header())
        self._logger.debug(response.text)
        payload = self._extract_payload(response)

        status = payload['server']['oper']['state']
        if status == 'Disabled':
            return STATUS_DISABLED
        if status == 'Up':
            return STATUS_ENABLED
        if status == 'Down':
            return STATUS_DOWN

        raise warthog.exceptions.WarthogNodeStatusError(
            'Unknown status of {0}: status={1}'.format(self._server, status))


class NodeActiveConnectionsCommand(_AuthenticatedCommand, _ResponseHandlerMixin):
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
        :raises warthog.exceptions.WarthogApiError: If the number of active
            connections to the server could not be determined for any other reason.
        """
        url = _get_endpoint_url(self._scheme_host, _PATH_CONNS)
        url = url.format(server=self._server)

        self._logger.debug('Making active connection count GET request for %s', self._server)
        response = self._transport.get(url, headers=self._auth_header())
        self._logger.debug(response.text)
        payload = self._extract_payload(response)

        return payload['server']['stats']['curr-conn']
