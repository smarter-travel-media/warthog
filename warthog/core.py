# -*- coding: utf-8 -*-

"""
"""
import logging

import requests
import warthog.exc


STATUS_ENABLED = 'enabled'

STATUS_DISABLED = 'disabled'

STATUS_TRANSITION = 'transition'

_API_VERSION = 'v2'

_ACTION_AUTHENTICATE = 'authenticate'

_ACTION_ENABLE = ''

_ACTION_DISABLE = ''

_ACTION_STATUS = 'slb.server.search'


class RequestsRunner(object):
    @staticmethod
    def get(*args, **kwargs):
        return requests.get(*args, **kwargs)

    @staticmethod
    def post(*args, **kwargs):
        return requests.post(*args, **kwargs)


class SessionStartCommand(object):
    logger = logging.getLogger('warthog')

    def __init__(self, scheme_host, username, password, runner=None):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._runner = runner if runner is not None else RequestsRunner()


    def send(self):
        url = get_base_url(self._scheme_host)
        params = get_base_query_params(_ACTION_AUTHENTICATE)
        params['username'] = self._username
        params['password'] = self._password

        self.logger.debug('Making session start request to %s', url)
        r = self._runner.get(url, params=params)

        json = r.json()
        if 'session_id' not in json:
            msg, code = _extract_error_message(json['response'])
            raise warthog.exc.WarthogAuthFailureError('Authentication failure', msg, code)
        return json['session_id']


class AuthenticatedCommand(object):
    logger = logging.getLogger('warthog')

    def __init__(self, scheme_host, session_id):
        self._scheme_host = scheme_host
        self._session_id = session_id

    def send(self, server):
        raise NotImplementedError()


class NodeEnableCommand(AuthenticatedCommand):
    def send(self, server):
        pass


class NodeDisableCommand(AuthenticatedCommand):
    def send(self, server):
        pass


class NodeStatusCommand(AuthenticatedCommand):
    def __init__(self, scheme_host, session_id, runner=None):
        super(NodeStatusCommand, self).__init__(scheme_host, session_id)
        self._runner = runner if runner is not None else RequestsRunner()

    def send(self, server):
        url = get_base_url(self._scheme_host)
        params = get_base_query_params(_ACTION_STATUS, self._session_id)
        params['name'] = server
        r = self._runner.get(url, params=params)

        json = r.json()
        if 'server' not in json:
            msg, code = _extract_error_message(json['response'])
            raise warthog.exc.WarthotNodeStatusError(
                'Could not get status of {0}'.format(server), msg, code)

        status = json['server']['status']
        if status:
            return STATUS_ENABLED
        return STATUS_DISABLED


def _extract_error_message(response):
    """

    :param response:
    :return:
    """
    if 'fail' == response['status']:
        return response['err']['msg'].strip(), response['err']['code']
    raise ValueError("Unexpected response format from request: {0}".format(response))


def get_base_url(scheme_host):
    return '/'.join([scheme_host, 'services', 'rest', _API_VERSION]) + '/'


def get_base_query_params(action, session_id=None):
    params = {
        'format': 'json',
        'method': action
    }

    if session_id is not None:
        params['session_id'] = session_id
    return params