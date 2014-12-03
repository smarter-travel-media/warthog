# -*- coding: utf-8 -*-

from click.testing import CliRunner

import pytest
import click
import requests

import warthog.cli
import warthog.exceptions


def test_main_no_command():
    runner = CliRunner()
    result = runner.invoke(warthog.cli.main)

    assert 0 == result.exit_code, "Expected zero exit code"


def test_main_bad_command():
    runner = CliRunner()
    result = runner.invoke(warthog.cli.main, args=['foo'])

    assert 0 != result.exit_code, "Expected non-zero exit code"


def test_main_default_config():
    runner = CliRunner()
    result = runner.invoke(warthog.cli.main, args=['default-config'])

    assert 0 == result.exit_code, 'Expected zero exit code'
    assert '[warthog]' in result.output, 'Expected "[warthog]" header in default config'


def test_main_config_path():
    runner = CliRunner()
    result = runner.invoke(warthog.cli.main, args=['config-path'])

    assert 0 == result.exit_code, 'Expected zero exit code'
    assert len(result.output), 'Expected at least some output'


def test_error_wrapper_no_such_node():
    @warthog.cli.error_wrapper
    def my_test_func(*_):
        raise warthog.exceptions.WarthogNoSuchNodeError(
            'No such server!', server='app1.example.com')

    with pytest.raises(click.BadParameter):
        my_test_func('something')


def test_error_wrapper_auth_failure():
    @warthog.cli.error_wrapper
    def my_test_func(*_):
        raise warthog.exceptions.WarthogAuthFailureError(
            'Authentication failed for some reason!')

    with pytest.raises(click.ClickException):
        my_test_func('something')


def test_error_wrapper_connection_error():
    @warthog.cli.error_wrapper
    def my_test_func(*_):
        raise requests.ConnectionError('No such LB host!')

    with pytest.raises(click.ClickException):
        my_test_func('something')

