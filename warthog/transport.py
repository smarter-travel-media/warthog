# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function, division

import ssl

import warnings

import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class TransportBuilder(object):
    def __init__(self, base=None):
        self._base = base if base is not None else requests.Session()

    def disable_verify(self):
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        self._base.verify = False
        return self

    def use_tlsv1(self):
        self._base.mount('https://', SSLTLSV1Adapter())
        return self

    def get(self):
        return self._base


class SSLTLSV1Adapter(HTTPAdapter):
    """"Transport adapter that allows us to use TLSv1 which is required
    for interacting with the A10 load balancer.
    """

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)
