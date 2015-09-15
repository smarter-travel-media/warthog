# -*- coding: utf-8 -*-


import ssl

import codecs
import pytest
import warthog.config
import warthog.exceptions
from warthog.packages.six.moves import configparser
import mock


class TestWarthogConfigLoader(object):
    def test_get_settings_not_parsed_yet(self):
        parser = mock.Mock(spec=warthog.config.WarthogConfigParser)
        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)

        with pytest.raises(RuntimeError):
            loader.get_settings()

    def test_get_settings_success(self):
        parser = mock.Mock(spec=warthog.config.WarthogConfigParser)
        parser.parse.return_value = warthog.config.WarthogConfigSettings(
            scheme_host='https://lb.example.com',
            username='username',
            password='password',
            verify=None,
            ssl_version=None
        )

        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)
        loader.initialize()
        settings = loader.get_settings()

        assert 'https://lb.example.com' == settings.scheme_host
        assert 'username' == settings.username
        assert 'password' == settings.password
        assert None is settings.verify
        assert None is settings.ssl_version


class TestWarthogConfigParser(object):
    def test_parse_no_config_file(self):
        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        open_impl = mock.MagicMock(spec=codecs.open)

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        with pytest.raises(warthog.exceptions.WarthogNoConfigFileError):
            parser.parse(None, 'utf-8', [])

    def test_parse_config_file_does_not_exist(self):
        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        open_impl = mock.MagicMock(spec=codecs.open)
        open_impl.side_effect = IOError("No such file!")

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        with pytest.raises(warthog.exceptions.WarthogNoConfigFileError):
            parser.parse('something.ini', 'utf-8', [])

    def test_parse_unicode_error(self):
        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        parser_impl.readfp.side_effect = UnicodeDecodeError('ascii', b'\x80abc', 0, 1, 'ordinal not in range(128)')
        open_impl = mock.MagicMock(spec=codecs.open)

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        with pytest.raises(warthog.exceptions.WarthogMalformedConfigFileError):
            parser.parse('something.ini', 'ascii', [])

    def test_parse_no_section(self):
        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        parser_impl.get.side_effect = configparser.NoSectionError('warthog')
        open_impl = mock.MagicMock(spec=codecs.open)

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        with pytest.raises(warthog.exceptions.WarthogMalformedConfigFileError):
            parser.parse('something.ini', 'utf-8', [])

    def test_parse_no_option(self):
        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        parser_impl.get.side_effect = configparser.NoOptionError('warthog', 'scheme_host')
        open_impl = mock.MagicMock(spec=codecs.open)

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        with pytest.raises(warthog.exceptions.WarthogMalformedConfigFileError):
            parser.parse('something.ini', 'utf-8', [])

    def test_parse_success(self):
        def has_option_impl(section, option):
            return True

        def get_impl(section, option):
            if option == 'scheme_host':
                return 'https://lb.example.com'
            if option == 'username':
                return 'user'
            if option == 'password':
                return 'pass'
            if option == 'ssl_version':
                return 'TLSv1'
            raise ValueError('No such option ' + option)

        def getboolean_impl(section, option):
            return True

        parser_impl = mock.Mock(spec=configparser.SafeConfigParser)
        parser_impl.has_option.side_effect = has_option_impl
        parser_impl.get.side_effect = get_impl
        parser_impl.getboolean.side_effect = getboolean_impl

        open_impl = mock.MagicMock(spec=codecs.open)

        parser = warthog.config.WarthogConfigParser(parser_impl=parser_impl, open_impl=open_impl)

        settings = parser.parse('something.ini', 'utf-8', [])

        assert 'https://lb.example.com' == settings.scheme_host
        assert 'user' == settings.username
        assert 'pass' == settings.password
        assert True == settings.verify
        assert ssl.PROTOCOL_TLSv1 == settings.ssl_version


class TestWarthogConfigResolver(object):
    def test_call_explicit_config_file(self):
        obj = warthog.config.WarthogConfigFileResolver([])

        assert '/tmp/something.ini' == obj('/tmp/something.ini')[0]

    def test_call_no_explicit_file_default_exists(self):
        default_file = '/etc/warthog.ini'
        exists = lambda x: x == default_file
        obj = warthog.config.WarthogConfigFileResolver(['/tmp/something.ini', default_file], exists_impl=exists)

        assert default_file == obj(None)[0]

    def test_call_no_explicit_file_default_does_not_exist(self):
        exists = lambda x: False
        obj = warthog.config.WarthogConfigFileResolver(['/tmp/something.ini', '/tmp/else.ini'], exists_impl=exists)

        assert None == obj(None)[0]


class FakeModule(object):
    """Class to wrap ``object`` so that we can set attributes on it
    but still get attribute errors for properties that aren't set, unlike
    :class:`mock.Mock` which will just hand back a mock instance
    """


def test_parse_ssl_version_none_input():
    assert None is warthog.config.parse_ssl_version(None)


def test_parse_ssl_version_blank_string():
    assert None is warthog.config.parse_ssl_version(u"    ")


def test_parse_ssl_version_empty_string():
    assert None is warthog.config.parse_ssl_version(u'')


def test_parse_ssl_version_valid_version():
    mod = FakeModule()
    mod.PROTOCOL_SSLv23 = 2
    mod.PROTOCOL_TLSv1 = 3
    mod.PROTOCOL_TLSv1_1 = 4
    mod.PROTOCOL_TLSv1_2 = 5

    assert mod.PROTOCOL_SSLv23 == warthog.config.parse_ssl_version(u'SSLv23', mod)
    assert mod.PROTOCOL_TLSv1 == warthog.config.parse_ssl_version(u'TLSv1', mod)
    assert mod.PROTOCOL_TLSv1_1 == warthog.config.parse_ssl_version(u'TLSv1_1', mod)
    assert mod.PROTOCOL_TLSv1_2 == warthog.config.parse_ssl_version(u'TLSv1_2', mod)


def test_parse_ssl_version_unsupported_version():
    mod = FakeModule()
    mod.PROTOCOL_TLSv1 = 3

    with pytest.raises(ValueError):
        warthog.config.parse_ssl_version(u'SSLv2', mod)

    with pytest.raises(ValueError):
        warthog.config.parse_ssl_version(u'TLSv1_1', mod)

    with pytest.raises(ValueError):
        warthog.config.parse_ssl_version(u'TLSv1_2', mod)


def test_parse_ssl_version_malformed_version():
    mod = FakeModule()
    mod.PROTOCOL_TLSv1 = 3

    with pytest.raises(ValueError):
        warthog.config.parse_ssl_version(u'SOMETHING', mod)

