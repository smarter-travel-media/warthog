# -*- coding: utf-8 -*-

import pytest
import requests
import mock

import warthog.core
import warthog.exceptions


SOME_CRAZY_ERROR = {
    'response': {
        'status': 'fail',
        'err': {
            'code': 10001,
            'msg': 'You done did it now'
        }
    }
}

BAD_PW = {
    'response': {
        'status': 'fail',
        'err': {
            'code': 520486915,
            'msg': 'Bad password'
        }
    }
}

INVALID_SESSION = {
    'response': {
        'status': 'fail',
        'err': {
            'code': 1009,
            'msg': 'Invalid session'
        }
    }
}

NO_SUCH_SERVER = {
    'response': {
        'status': 'fail',
        'err': {
            'code': 67174402,
            'msg': 'That server does not exist'
        }
    }
}

OK_RESPONSE = {
    'response': {
        'status': 'OK'
    }
}

NODE_STATUS = {
    'server_stat': {
        'status': 1,
        'cur_conns': 42
    }
}

SCHEME_HOST = 'https://lb.example.com'


@pytest.fixture
def response():
    return mock.Mock(spec=requests.Response)


@pytest.fixture
def transport(response):
    mock_transport = mock.Mock(spec=requests.Session)
    mock_transport.get.return_value = response
    mock_transport.post.return_value = response
    return mock_transport


class TestSessionStartCommand(object):
    def test_send_bad_password(self, transport, response):
        response.text = ''
        response.json.return_value = dict(BAD_PW)

        with pytest.raises(warthog.exceptions.WarthogAuthFailureError):
            cmd = warthog.core.SessionStartCommand(transport, SCHEME_HOST, 'user', 'bad password')
            cmd.send()

        assert transport.post.called, 'Expected transport ".get()" to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.json.return_value = {
            'session_id': '1234'
        }

        cmd = warthog.core.SessionStartCommand(transport, SCHEME_HOST, 'user', 'password')
        session = cmd.send()

        assert '1234' == session, 'Did not get expected session ID'


class TestSessionEndCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, 'bad session')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogAuthCloseError):
            cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, '1234')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.json.return_value = dict(OK_RESPONSE)

        cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, '1234')
        closed = cmd.send()
        assert closed, 'Did not get expected True result from session close'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeEnableCommand(object):

    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogNodeEnableError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.json.return_value = dict(OK_RESPONSE)

        cmd = warthog.core.NodeEnableCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        got_enabled = cmd.send()
        assert got_enabled, 'Did not get get expected True result from node enable'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeDisableCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogNodeDisableError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.json.return_value = dict(OK_RESPONSE)

        cmd = warthog.core.NodeDisableCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        got_disabled = cmd.send()
        assert got_disabled, 'Did not get get expected True result from node disable'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeStatusCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogNodeStatusError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_enabled(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NODE_STATUS)

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_ENABLED == status, 'Did not get expected enabled status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_disabled(self, transport, response):
        payload = dict(NODE_STATUS)
        payload['server_stat']['status'] = 0

        response.text = ''
        response.json.return_value = payload

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_DISABLED == status, 'Did not get expected disabled status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_down(self, transport, response):
        payload = dict(NODE_STATUS)
        payload['server_stat']['status'] = 2

        response.text = ''
        response.json.return_value = payload

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_DOWN == status, 'Did not get expected down status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_no_known_status(self, transport, response):
        payload = dict(NODE_STATUS)
        payload['server_stat']['status'] = 999

        response.text = ''
        response.json.return_value = payload

        with pytest.raises(warthog.exceptions.WarthogNodeStatusError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'


class TestNodeActiveConnectionsCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogNodeStatusError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.json.return_value = dict(NODE_STATUS)

        cmd = warthog.core.NodeActiveConnectionsCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        connections = cmd.send()
        assert 42 == connections, 'Did not get expected active connections'
        assert transport.get.called, 'Expected transport ".get() to be called'

