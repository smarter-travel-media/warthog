# -*- coding: utf-8 -*-

import ssl

import warthog.ssl


# Test our hacky constants to make sure we haven't shot ourselves in the
# foot in a completely obvious and predictable way.


def test_ssl3_matches():
    assert ssl.PROTOCOL_SSLv3 == warthog.ssl.PROTOCOL_SSLv3


def test_ssl23_matches():
    assert ssl.PROTOCOL_SSLv23 == warthog.ssl.PROTOCOL_SSLv23


def test_tls1_matches():
    assert ssl.PROTOCOL_TLSv1 == warthog.ssl.PROTOCOL_TLSv1


def test_tls_matches_ssl23():
    # New constant in Python 2.7.13 for negotiation of the highest
    # supported protocol. Same value as the previous "negotiate"
    # constant (SSLv23).
    assert ssl.PROTOCOL_SSLv23 == warthog.ssl.PROTOCOL_TLS


def test_tls_matches():
    try:
        # It's possible that we're running under an old version of Python
        # and this constant doesn't exist (hence why warthog.ssl exists).
        module_const = ssl.PROTOCOL_TLS
    except AttributeError:
        return

    assert module_const == warthog.ssl.PROTOCOL_TLS

    
def test_tls1_1_matches():
    try:
        # It's possible that we're running under an old version of Python
        # and this constant doesn't exist (hence why warthog.ssl exists).
        module_const = ssl.PROTOCOL_TLSv1_1
    except AttributeError:
        return

    assert module_const == warthog.ssl.PROTOCOL_TLSv1_1


def test_tls1_2_matches():
    try:
        # It's possible that we're running under an old version of Python
        # and this constant doesn't exist (hence why warthog.ssl exists).
        module_const = ssl.PROTOCOL_TLSv1_2
    except AttributeError:
        return

    assert module_const == warthog.ssl.PROTOCOL_TLSv1_2
