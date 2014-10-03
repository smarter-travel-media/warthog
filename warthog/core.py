# -*- coding: utf-8 -*-

"""
"""
import logging
import urlparse

import warthog.exc


STATUS_ENABLED = 'enabled'

STATUS_DISABLED = 'disabled'

ERROR_CODE_GRACEFUL_SHUTDOWN = 67174416

TRANSIENT_ERRORS = frozenset([
    ERROR_CODE_GRACEFUL_SHUTDOWN
])

_API_VERSION = 'v2'

_ACTION_AUTHENTICATE = 'authenticate'

_ACTION_ENABLE = _ACTION_DISABLE = 'slb.server.update'

_ACTION_STATUS = _ACTION_STATISTICS = 'slb.server.fetchStatistics'

_ACTION_CLOSE_SESSION = 'session.close'


def get_log():
    return logging.getLogger('warthog')


class SessionStartCommand(object):
    """

    """
    _logger = get_log()

    def __init__(self, transport, scheme_host, username, password):
        """
        """
        self._transport = transport
        self._scheme_host = scheme_host
        self._username = username
        self._password = password

    def send(self):
        """
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
            raise warthog.exc.WarthogAuthFailureError(
                'Authentication failure with {0}'.format(self._scheme_host), msg, code)
        return json['session_id']


class _AuthenticatedCommand(object):
    """

    """
    _logger = get_log()

    def __init__(self, transport, scheme_host, session_id):
        """
        """
        self._transport = transport
        self._scheme_host = scheme_host
        self._session_id = session_id

    def send(self, *args):
        """
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
            raise warthog.exc.WarthogAuthCloseError(
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
            raise warthog.exc.WarthogNodeEnableError(
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
            raise warthog.exc.WarthogNodeDisableError(
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
            raise warthog.exc.WarthogNodeStatusError(
                'Could not get status of {0}'.format(server), msg, code)

        status = json['server_stat']['status']
        if status == 0:
            return STATUS_DISABLED
        if status == 1:
            return STATUS_ENABLED
        raise warthog.exc.WarthogNodeStatusError(
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
            raise warthog.exc.WarthogNodeStatusError(
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