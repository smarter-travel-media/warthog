# -*- coding: utf-8 -*-
#
# Warthog - Client for A10 load balancers
#
# Copyright 2014 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.transport
~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function, division

import ssl

import warnings

import requests

from requests.adapters import (
    HTTPAdapter,
    DEFAULT_POOLBLOCK,
    DEFAULT_POOLSIZE,
    DEFAULT_RETRIES)
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Default to using the SSL/TLS version that the A10 requires instead of
# the default that the requests/urllib3 library picks.
DEFAULT_SSL_VERSION = ssl.PROTOCOL_TLSv1


def get_transport(verify=True, ssl_version=DEFAULT_SSL_VERSION):
    """Get a :class:`requests.Session` instance that has been configured
    according to the given parameters.

    :param bool verify: Should SSL certificates by verified when connecting
        over HTTPS? Default is ``True``. If you have chosen not to verify certificates
        warnings about this emitted by the requests library will be suppressed.
    :param int ssl_version: Explicit version of SSL to use for HTTPS connections
        to an A10 load balancer. The version is a constant as specified by the
        :mod:`ssl` module (PROTOCOL_XXX). Default is TLSv1. If you don't wish to
        use a specific version and instead rely on the default for the requests /
        urllib3 module, pass ``ssl_version=None``.
    :return: Configured session instance for making HTTP(S) requests
    :rtype: requests.Session
    """
    transport = requests.Session()

    if not verify:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        transport.verify = False

    if ssl_version is not None:
        transport.mount('https://', VersionedSSLAdapter(ssl_version))
    return transport


class VersionedSSLAdapter(HTTPAdapter):
    """"Transport adapter that requires the use of a specific version of SSL."""

    def __init__(self, ssl_version, pool_connections=DEFAULT_POOLSIZE,
                 pool_maxsize=DEFAULT_POOLSIZE, max_retries=DEFAULT_RETRIES,
                 pool_block=DEFAULT_POOLBLOCK):
        self._ssl_version = ssl_version

        super(VersionedSSLAdapter, self).__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block,
            ssl_version=self._ssl_version, **pool_kwargs)
