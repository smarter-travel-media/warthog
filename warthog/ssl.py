# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2016 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.ssl
~~~~~~~~~~~

SSL related constants used by Warthog
"""

# Define our own versions of expected constants in the Python ssl
# module since older Python versions didn't define all of them. For
# example Python 2.6 and Python 3.3 don't include TLSv1.1 or TLSv1.2
# and we need to support the combination of those Python versions
# and TLS versions. Kinda hacky but required. Such is life.

PROTOCOL_SSLv3 = 1

PROTOCOL_SSLv23 = 2

PROTOCOL_TLSv1 = 3

PROTOCOL_TLSv1_1 = 4

PROTOCOL_TLSv1_2 = 5
