# -*- coding: utf-8 -*-
#
# Warthog - Client for A10 load balancers
#
# Copyright 2014 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.core
~~~~~~~~~~~~

Basic building blocks for authentication and interaction with a load balancer.
"""

import logging
import urlparse

import warthog.exceptions


STATUS_ENABLED = 'enabled'

STATUS_DISABLED = 'disabled'

ERROR_CODE_GRACEFUL_SHUTDOWN = 67174416

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


class SessionStartCommand(object):
    """Command to authenticate with the load balancer and start a new session
    to be used by subsequent commands.
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

        self._logger.debug('Making session start request to %s', url)
        r = self._transport.get(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if 'session_id' not in json:
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogAuthFailureError(
                'Authentication failure with {0}'.format(self._scheme_host), msg, code)
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

    def send(self, *args):
        """Abstract method for making a request to the load balancer API and parsing
        the result and returning any meaningful information (implementation specific).
        """
        raise NotImplementedError()


class SessionEndCommand(_AuthenticatedCommand):
    """



    """

    def send(self):
        """


        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_CLOSE_SESSION, self._session_id)

        self._logger.debug('Making session close request to %s', url)
        r = self._transport.post(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if json['response']['status'] == 'fail':
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogAuthCloseError(
                'Could not close session {0} on {1}'.format(
                    self._session_id, self._scheme_host), msg, code)
        return True


class NodeEnableCommand(_AuthenticatedCommand):
    """

    """

    def send(self, server):
        """
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_ENABLE, self._session_id)
        params['name'] = server
        params['server'] = server
        params['status'] = 1

        self._logger.debug('Making node enable request for %s', server)
        r = self._transport.post(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if json['response']['status'] == 'fail':
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogNodeEnableError(
                'Could not enable node {0}'.format(server), msg, code)
        return True


class NodeDisableCommand(_AuthenticatedCommand):
    """

    """

    def send(self, server):
        """
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_ENABLE, self._session_id)
        params['name'] = server
        params['server'] = server
        params['status'] = 0

        self._logger.debug('Making node disable request for %s', server)
        r = self._transport.post(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if json['response']['status'] == 'fail':
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogNodeDisableError(
                'Could not disable node {0}'.format(server), msg, code)
        return True


class NodeStatusCommand(_AuthenticatedCommand):
    """

    """

    def send(self, server):
        """
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_STATUS, self._session_id)
        params['name'] = server

        self._logger.debug('Making node status request for %s', server)
        r = self._transport.get(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if 'server_stat' not in json:
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogNodeStatusError(
                'Could not get status of {0}'.format(server), msg, code)

        status = json['server_stat']['status']
        if status == 0:
            return STATUS_DISABLED
        if status == 1:
            return STATUS_ENABLED
        raise warthog.exceptions.WarthogNodeStatusError(
            'Unknown status of {0}: status={1}'.format(server, status))


class NodeActiveConnectionsCommand(_AuthenticatedCommand):
    """




    """

    def send(self, server):
        """
        """
        url = _get_base_url(self._scheme_host)
        params = _get_base_query_params(_ACTION_STATISTICS, self._session_id)
        params['name'] = server

        self._logger.debug('Making active connection count request for %s', server)
        r = self._transport.get(url, params=params)
        self._logger.debug(r.text)
        json = r.json()

        if 'server_stat' not in json:
            msg, code = _extract_error_message(json['response'])
            raise warthog.exceptions.WarthogNodeStatusError(
                'Could not get active connection count of {0}'.format(server), msg, code)
        return json['server_stat']['cur_conns']


def _extract_error_message(response):
    """

    :param response:
    :return:
    """
    if response['status'] == 'fail':
        return response['err']['msg'].strip(), response['err']['code']
    raise ValueError(
        "Unexpected response format from request: {0}".format(response))


def _get_base_url(scheme_host):
    """


    :param scheme_host:
    :return:
    """
    return urlparse.urljoin(
        scheme_host, 'services/rest/{version}/'.format(version=_API_VERSION))


def _get_base_query_params(action, session_id=None):
    """

    :param action:
    :param session_id:
    :return:
    """
    params = {
        'format': 'json',
        'method': action
    }

    if session_id is not None:
        params['session_id'] = session_id
    return params