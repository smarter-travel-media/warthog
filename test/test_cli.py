# -*- coding: utf-8 -*-

import io

import codecs
import os.path
import click
import pytest
import mock
import warthog.cli
from warthog.six import text_type
from warthog.six.moves import configparser


def test_get_config_location_cli_location():
    location = warthog.cli.get_config_location('some/path')

    assert 'some/path' == location, 'Did not get expected CLI location'


def test_get_config_location_default_location(monkeypatch):
    path_exists = mock.MagicMock()
    path_exists.side_effect = [False, True]

    monkeypatch.setattr(os.path, 'exists', path_exists)
    location = warthog.cli.get_config_location(None)
    assert '/etc/warthog.ini' == location, 'Did not get expected config location'


def test_get_config_location_no_config_file(monkeypatch):
    path_exists = mock.MagicMock()
    path_exists.return_value = None

    monkeypatch.setattr(os.path, 'exists', path_exists)
    location = warthog.cli.get_config_location(None)
    assert location is None, 'Did not get expected None config location'


def test_get_parser_no_location():
    with pytest.raises(click.BadParameter):
        warthog.cli.get_parser(None)


def test_get_parser_io_error(monkeypatch):
    file_open = mock.MagicMock()
    file_open.side_effect = IOError("OH NO!")

    monkeypatch.setattr(codecs, 'open', file_open)

    with pytest.raises(click.BadParameter):
        warthog.cli.get_parser("some/file.ini")


def test_get_parser_missing_headers(monkeypatch):
    file_stream = io.StringIO(warthog.six.text_type("blah"))
    file_open = mock.MagicMock()
    file_open.return_value = file_stream

    monkeypatch.setattr(codecs, 'open', file_open)

    with pytest.raises(click.BadParameter):
        warthog.cli.get_parser("some/file.ini")


def test_get_parser_valid_config_file(monkeypatch):
    file_stream = io.StringIO(text_type("""\
[warthog]
scheme_host = https://lb.example.com
username = username
password = password
verify = yes
"""))

    file_open = mock.MagicMock()
    file_open.return_value = file_stream

    monkeypatch.setattr(codecs, 'open', file_open)

    parser = warthog.cli.get_parser("some/file.ini")
    assert isinstance(parser, configparser.RawConfigParser)


def test_parse_config_no_section():
    error = configparser.NoSectionError('warthog')

    mock_parser = mock.Mock(spec=configparser.SafeConfigParser)
    mock_parser.get.side_effect = error

    with pytest.raises(click.BadParameter):
        warthog.cli.parse_config(mock_parser)


def test_parse_config_missing_option():
    error = configparser.NoOptionError("scheme_host", "warthog")

    mock_parser = mock.Mock(spec=configparser.SafeConfigParser)
    mock_parser.get.side_effect = error

    with pytest.raises(click.BadParameter):
        warthog.cli.parse_config(mock_parser)


def test_parse_config_valid_config():
    mock_parser = mock.Mock(spec=configparser.SafeConfigParser)
    mock_parser.get.side_effect = [
        'https://lb.example.com', 'someuser', 'password']
    mock_parser.getboolean.return_value = True

    settings = warthog.cli.parse_config(mock_parser)

    assert 'https://lb.example.com' == settings.scheme_host
    assert 'someuser' == settings.username
    assert 'password' == settings.password
    assert settings.verify
