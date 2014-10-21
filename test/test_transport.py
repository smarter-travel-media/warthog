# -*- coding: utf-8 -*-

import ssl

import warthog.transport


def test_get_transport_factory_no_verify():
    factory = warthog.transport.get_transport_factory(verify=False)
    session = factory()
    adapter = session.get_adapter('https://lb.example.com')

    assert isinstance(
        adapter, warthog.transport.VersionedSSLAdapter), 'Did not get expected HTTPS adapter'
    assert not session.verify, 'Expected verify to be disabled on session'


def test_get_transport_factory_alternate_ssl_version():
    factory = warthog.transport.get_transport_factory(ssl_version=ssl.PROTOCOL_SSLv3)
    session = factory()
    adapter = session.get_adapter('https://lb.example.com')

    assert ssl.PROTOCOL_SSLv3 == adapter.ssl_version, 'Did not get expected SSL version'
