# -*- coding: utf-8 -*-


import uuid

import codecs

import os.path
import pytest
import mock
import warthog.config
from warthog.six.moves import configparser


class TestWarthogConfigLoader(object):
    def test_parse_configuration_no_explict_config_no_default_config(self, monkeypatch):
        path_exists = mock.MagicMock()
        path_exists.return_value = False

        monkeypatch.setattr(os.path, 'exists', path_exists)

        loader = warthog.config.WarthogConfigLoader()

        with pytest.raises(ValueError):
            loader.parse_configuration()

    def test_parse_configuration_explicit_config_file_does_not_exist(self):
        loader = warthog.config.WarthogConfigLoader(config_file=str(uuid.uuid4()))

        with pytest.raises(IOError):
            loader.parse_configuration()

    def test_parse_configuration_cannot_read_file(self, monkeypatch):
        parser = mock.Mock(spec=configparser.SafeConfigParser)
        parser.readfp.side_effect = IOError("OH NO!")

        codecs_open = mock.MagicMock()
        monkeypatch.setattr(codecs, 'open', codecs_open)

        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)

        with pytest.raises(IOError):
            loader.parse_configuration()

    def test_parse_configuration_no_section(self, monkeypatch):
        parser = mock.Mock(spec=configparser.SafeConfigParser)
        parser.get.side_effect = configparser.NoSectionError('warthog')

        codecs_open = mock.MagicMock()
        monkeypatch.setattr(codecs, 'open', codecs_open)

        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)

        with pytest.raises(RuntimeError):
            loader.parse_configuration()

    def test_parse_configuration_no_option(self, monkeypatch):
        parser = mock.Mock(spec=configparser.SafeConfigParser)
        parser.get.side_effect = configparser.NoOptionError('warthog', 'scheme_host')

        codecs_open = mock.MagicMock()
        monkeypatch.setattr(codecs, 'open', codecs_open)

        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)

        with pytest.raises(RuntimeError):
            loader.parse_configuration()

    def test_parse_configuration_success(self, monkeypatch):
        def get_vals(_, option):
            if option == 'scheme_host':
                return 'https://lb.example.com'
            if option == 'username':
                return 'username'
            if option == 'password':
                return 'password'
            raise ValueError("No such option: {0}".format(option))

        parser = mock.Mock(spec=configparser.SafeConfigParser)
        parser.get.side_effect = get_vals
        parser.getboolean.return_value = True

        codecs_open = mock.MagicMock()
        monkeypatch.setattr(codecs, 'open', codecs_open)

        loader = warthog.config.WarthogConfigLoader(config_file='warthog.ini', config_parser=parser)
        settings = loader.parse_configuration()

        assert 'https://lb.example.com' == settings.scheme_host
        assert 'username' == settings.username
        assert 'password' == settings.password
        assert settings.verify
