# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function, division


class WarthogError(Exception):
    def __init__(self, msg, api_msg=None, api_code=None):
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
        return '{clazz}({msg}, {api_msg}, {api_code})'.format(
            clazz=self.__class__.__name__, msg=self.msg, api_msg=self.api_msg,
            api_code=self.api_code)


class WarthogAuthFailureError(WarthogError):
    pass


class WarthogNodeStatusError(WarthogError):
    pass


class WarthogNodeEnableError(WarthogError):
    pass


class WarthogNodeDisableError(WarthogError):
    pass


class WarthogAuthCloseError(WarthogError):
    pass
