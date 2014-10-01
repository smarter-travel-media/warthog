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

_ACTION_STATUS = ''


class RequestsRunner(object):
    @staticmethod
    def get(*args, **kwargs):
        return requests.get(*args, **kwargs)

    @staticmethod
    def post(*args, **kwargs):
        return requests.post(*args, **kwargs)


class SessionStartRequest(object):
    logger = logging.getLogger('warthog')

    def __init__(self, scheme_host, username, password, runner=None):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._runner = runner if runner is not None else RequestsRunner()

    @staticmethod
    def _extract_error_message(response):
        """

        :param response:
        :return:
        """
        if 'fail' == response['status']:
            return response['err']['msg'].strip(), response['err']['code']
        raise ValueError("Unexpected response format from authentication: {0}".format(response))

    def send(self):
        url = get_base_url(self._scheme_host)
        params = get_base_query_params(_ACTION_AUTHENTICATE)
        params['username'] = self._username
        params['password'] = self._password

        self.logger.debug('Making session start request to %s', url)
        r = self._runner.get(url, params=params)

        if r.status_code != requests.codes['ok']:
            raise warthog.exc.WarthogAuthFailureError(
                'Authentication failure. HTTP status {0}: {1}'.format(
                    r.status_code, r.text))

        json = r.json()
        if 'session_id' not in json:
            msg, code = self._extract_error_message(json['response'])
            raise warthog.exc.WarthogAuthFailureError('Authentication failure', msg, code)
        return json['session_id']


class AuthenticatedRequest(object):
    logger = logging.getLogger('warthog')

    def __init__(self, scheme_host, session_id):
        self._scheme_host = scheme_host
        self._session_id = session_id

    def send(self):
        pass


class NodeEnableRequest(AuthenticatedRequest):
    pass


class NodeDisableRequest(AuthenticatedRequest):
    pass


class NodeStatusRequest(AuthenticatedRequest):
    pass


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