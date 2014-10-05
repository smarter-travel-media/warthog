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


def get_transport(verify=True, use_tlsv1=True):
    transport = requests.Session()

    if not verify:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        transport.verify = False

    if use_tlsv1:
        transport.mount('https://', SSLTLSV1Adapter())

    return transport


class SSLTLSV1Adapter(HTTPAdapter):
    """"Transport adapter that allows us to use TLSv1 which is required
    for interacting with the A10 load balancer.
    """

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block,
            ssl_version=ssl.PROTOCOL_TLSv1, **pool_kwargs)
