# -*- coding: utf-8 -*-

"""
"""

_API_VERSION = 'v2'


class SessionStartRequest(object):
    def __init__(self, scheme_host, username, password):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password

    def __call__(self, *args, **kwargs):
        pass


class AuthenticatedRequest(object):
    def __init__(self, scheme_host, session_id):
        self._session_id = session_id
        self._scheme_host = scheme_host

    def __call__(self, *args, **kwargs):
        pass


class NodeEnableRequest(AuthenticatedRequest):
    pass


class NodeDisableRequest(AuthenticatedRequest):
    pass


class NodeStatusRequest(AuthenticatedRequest):
    pass


