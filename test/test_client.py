# -*- coding: utf-8 -*-

import logging

import pytest
import mock
import warthog.client
import warthog.core
import warthog.exceptions


SCHEME_HOST = 'https://lb.example.com'


@pytest.fixture
def commands(
        start_cmd,
        end_cmd,
        status_cmd,
        conn_cmd,
        enable_cmd,
        disable_cmd):
    factory = mock.Mock(spec=warthog.client.CommandFactory)
    factory.get_session_start.return_value = start_cmd
    factory.get_session_end.return_value = end_cmd
    factory.get_server_status.return_value = status_cmd
    factory.get_enable_server.return_value = enable_cmd
    factory.get_disable_server.return_value = disable_cmd
    factory.get_active_connections.return_value = conn_cmd
    return factory


@pytest.fixture
def start_cmd():
    return mock.Mock(spec=warthog.core.SessionStartCommand)


@pytest.fixture
def end_cmd():
    return mock.Mock(spec=warthog.core.SessionEndCommand)


@pytest.fixture
def status_cmd():
    return mock.Mock(spec=warthog.core.NodeStatusCommand)


@pytest.fixture
def conn_cmd():
    return mock.Mock(spec=warthog.core.NodeActiveConnectionsCommand)


@pytest.fixture
def enable_cmd():
    return mock.Mock(spec=warthog.core.NodeEnableCommand)


@pytest.fixture
def disable_cmd():
    return mock.Mock(spec=warthog.core.NodeDisableCommand)


@pytest.fixture
def client():
    return mock.Mock(spec=warthog.client.WarthogClient)


def test_session_context_enter_yields_session(commands, start_cmd):
    start_cmd.send.return_value = '1234'

    context = warthog.client.session_context(SCHEME_HOST, 'user', 'password', commands)
    session = context.__enter__()

    assert '1234' == session, 'Did not get expected session ID'
    commands.get_session_start.assert_called_once_with(SCHEME_HOST, 'user', 'password')
    assert start_cmd.send.called, 'Expected session start .send() to be called'


def test_session_context_exit_closes_previous_session(commands, start_cmd, end_cmd):
    start_cmd.send.return_value = '1234'

    context = warthog.client.session_context(SCHEME_HOST, 'user', 'password', commands)
    context.__enter__()
    context.__exit__(None, None, None)

    commands.get_session_end.assert_called_once_with(SCHEME_HOST, '1234')
    assert end_cmd.send.called, 'Expected session end .send() to be called'


def test_session_context_exception_in_context_propagated(commands, start_cmd):
    start_cmd.send.return_value = '1234'
    context = warthog.client.session_context(SCHEME_HOST, 'user', 'password', commands)

    with pytest.raises(RuntimeError):
        with context:
            raise RuntimeError("AHH!")


class TestWarthogClient(object):
    def test_get_status(self, commands, start_cmd, end_cmd, status_cmd):
        start_cmd.send.return_value = '1234'
        status_cmd.send.return_value = 'down'

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        status = client.get_status('app1.example.com')

        assert 'down' == status, 'Did not get expected status'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_get_connections(self, commands, start_cmd, end_cmd, conn_cmd):
        start_cmd.send.return_value = '1234'
        conn_cmd.send.return_value = 42

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        connections = client.get_connections('app1.example.com')

        assert 42 == connections, 'Did not get expected active connections'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_disable_server_no_active_connections(self, commands, start_cmd, end_cmd,
                                                  status_cmd, conn_cmd, disable_cmd):
        start_cmd.send.return_value = '1234'
        disable_cmd.send.return_value = True
        conn_cmd.send.return_value = 0
        status_cmd.send.return_value = 'disabled'

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        disabled = client.disable_server('app1.example.com')

        assert disabled, 'Server did not end up disabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_disable_server_with_active_connections(self, commands, start_cmd, end_cmd,
                                                    status_cmd, conn_cmd, disable_cmd):
        start_cmd.send.return_value = '1234'
        disable_cmd.send.return_value = True
        conn_cmd.send.return_value = [42, 3, 0]
        status_cmd.send.return_value = 'disabled'

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        disabled = client.disable_server('app1.example.com')

        assert disabled, 'Server did not end up disabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_disable_server_never_gets_disabled(self, commands, start_cmd, end_cmd,
                                                status_cmd, conn_cmd, disable_cmd):
        start_cmd.send.return_value = '1234'
        disable_cmd.send.return_value = True
        conn_cmd.send.return_value = 42
        status_cmd.send.return_value = 'enabled'

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        disabled = client.disable_server('app1.example.com')

        assert not disabled, 'Server ended up disabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_enable_server_in_graceful_shutdown(self, commands, start_cmd, end_cmd,
                                                status_cmd, enable_cmd):
        graceful_error = warthog.exceptions.WarthogNodeEnableError(
            '', api_code=warthog.core.ERROR_CODE_GRACEFUL_SHUTDOWN, api_msg='')

        start_cmd.send.return_value = '1234'
        enable_cmd.send.side_effect = [graceful_error, graceful_error, True]
        status_cmd.send.return_value = 'enabled'

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        enabled = client.enable_server('app1.example.com')

        assert enabled, 'Server did not end up enabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_enable_server_in_graceful_shutdown_switching_to_down(self, commands, start_cmd, end_cmd,
                                                                  status_cmd, enable_cmd):
        graceful_error = warthog.exceptions.WarthogNodeEnableError(
            '', api_code=warthog.core.ERROR_CODE_GRACEFUL_SHUTDOWN, api_msg='')

        start_cmd.send.return_value = '1234'
        enable_cmd.send.side_effect = [graceful_error, graceful_error, True]
        status_cmd.send.side_effect = ['down', 'down', 'enabled', 'enabled']

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        enabled = client.enable_server('app1.example.com')

        assert enabled, 'Server did not end up enabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_enable_server_no_graceful_shutdown_switching_to_down(self, commands, start_cmd, end_cmd,
                                                                  status_cmd, enable_cmd):
        start_cmd.send.return_value = '1234'
        enable_cmd.send.return_value = True
        status_cmd.send.side_effect = ['down', 'down', 'enabled', 'enabled']

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        enabled = client.enable_server('app1.example.com')

        assert enabled, 'Server did not end up enabled'
        assert end_cmd.send.called, 'Session end .send() did not get called'

    def test_enable_server_never_comes_out_of_graceful_shutdown(self, commands, start_cmd, end_cmd,
                                                                enable_cmd):
        graceful_error = warthog.exceptions.WarthogNodeEnableError(
            '', api_code=warthog.core.ERROR_CODE_GRACEFUL_SHUTDOWN, api_msg='')

        start_cmd.send.return_value = '1234'
        enable_cmd.send.side_effect = [graceful_error, graceful_error]

        client = warthog.client.WarthogClient(
            SCHEME_HOST, 'user', 'password', wait_interval=0.1, commands=commands)

        with pytest.raises(warthog.exceptions.WarthogNodeEnableError):
            client.enable_server('app1.example.com', max_retries=1)

        assert end_cmd.send.called, 'Session end .send() did not get called'
