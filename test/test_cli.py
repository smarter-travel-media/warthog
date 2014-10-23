# -*- coding: utf-8 -*-

from click.testing import CliRunner

import warthog.cli


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

