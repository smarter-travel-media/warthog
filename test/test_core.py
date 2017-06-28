# -*- coding: utf-8 -*-

import mock
import pytest
import requests

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

AUTH_SUCCESS = {
    "authresponse": {
        "signature": "ad44c3dfbac9440da876e7b3feaf1fc",
        "description": "the signature should be set in Authorization header for following request."
    }
}

BAD_PW = {
    "authorizationschema": {
        "code": 403,
        "error": "Incorrect user name or password",
        "auth_uri": "/axapi/v3/auth",
        "logoff_uri": "/axapi/v3/logoff",
        "username": "required",
        "password": "required"
    }
}

INVALID_SESSION = {
    "authorizationschema": {
        "code": 401,
        "error": "Invalid admin session.",
        "auth_uri": "/axapi/v3/auth",
        "logoff_uri": "/axapi/v3/logoff",
        "username": "required",
        "password": "required"
    }
}

NO_PERMISSIONS = {
    "response": {
        "status": "fail",
        "err": {
            "code": 419545856,
            "from": "BACKEND",
            "msg": "No write privilege of this admin session."
        }
    }
}

NO_SUCH_SERVER = {
    "response": {
        "status": "fail",
        "err": {
            "code": 1023460352,
            "from": "CM",
            "msg": "Object specified does not exist (object: server)"
        }
    }
}

OK_RESPONSE = {
    'response': {
        'status': 'OK'
    }
}

NODE_OPER = {
    "server": {
        "oper": {
            "state": "Up"
        },
        "port-list": [
            {
                "oper": {
                    "state": "Up"
                },
                "a10-url": "/axapi/v3/slb/server/app1.example.com/port/80+tcp/oper",
                "port-number": 80,
                "protocol": "tcp"
            }
        ],
        "a10-url": "/axapi/v3/slb/server/app1.example.com/oper",
        "name": "app1.example.com"
    }
}

NODE_STATS = {
    "server": {
        "stats": {
            "curr-conn": 0,
            "total-conn": 0,
            "fwd-pkt": 0,
            "rev-pkt": 0,
            "peak-conn": 0,
            "total_req": 0,
            "total_req_succ": 0,
            "curr_ssl_conn": 0,
            "total_ssl_conn": 0,
            "total_fwd_bytes": 0,
            "total_rev_bytes": 0
        },
        "port-list": [
            {
                "stats": {
                    "curr_conn": 0,
                    "curr_req": 0,
                    "total_req": 0,
                    "total_req_succ": 0,
                    "total_fwd_bytes": 0,
                    "total_fwd_pkts": 0,
                    "total_rev_bytes": 0,
                    "total_rev_pkts": 0,
                    "total_conn": 0,
                    "last_total_conn": 0,
                    "peak_conn": 0,
                    "es_resp_200": 0,
                    "es_resp_300": 0,
                    "es_resp_400": 0,
                    "es_resp_500": 0,
                    "es_resp_other": 0,
                    "es_req_count": 0,
                    "es_resp_count": 0,
                    "es_resp_invalid_http": 0,
                    "total_rev_pkts_inspected": 0,
                    "total_rev_pkts_inspected_good_status_code": 0,
                    "response_time": 0,
                    "fastest_rsp_time": 0,
                    "slowest_rsp_time": 0,
                    "curr_ssl_conn": 0,
                    "total_ssl_conn": 0
                },
                "a10-url": "/axapi/v3/slb/server/app1.example.com/port/80+tcp/stats",
                "port-number": 80,
                "protocol": "tcp"
            }
        ],
        "a10-url": "/axapi/v3/slb/server/app1.example.com/stats",
        "name": "app1.example.com"
    }
}

NODE_ALTER = {
    "server": {
        "name": "app1.example.com",
        "host": "10.0.0.1",
        "action": "enable",
        "template-server": "default",
        "health-check-disable": 0,
        "conn-limit": 8000000,
        "no-logging": 0,
        "weight": 1,
        "slow-start": 0,
        "spoofing-cache": 0,
        "stats-data-action": "stats-data-enable",
        "extended-stats": 0,
        "uuid": "7bdeee5c-56f0-44b5-a040-243a389f6fd1",
        "port-list": [
            {
                "port-number": 80,
                "protocol": "tcp",
                "range": 0,
                "template-port": "default",
                "action": "enable",
                "no-ssl": 0,
                "health-check-disable": 0,
                "weight": 1,
                "conn-limit": 8000000,
                "no-logging": 0,
                "stats-data-action": "stats-data-enable",
                "extended-stats": 0,
                "uuid": "7bdeee5c-56f0-44b5-a040-243a389f6fd1",
                "a10-url": "/axapi/v3/slb/server/app1.example.com/port/80+tcp"
            }
        ]
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
        response.status_code = 403
        response.ok = False
        response.json.return_value = dict(BAD_PW)

        with pytest.raises(warthog.exceptions.WarthogAuthFailureError):
            cmd = warthog.core.SessionStartCommand(transport, SCHEME_HOST, 'user', 'bad password')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post()" to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = dict(AUTH_SUCCESS)

        cmd = warthog.core.SessionStartCommand(transport, SCHEME_HOST, 'user', 'password')
        session = cmd.send()

        assert 'ad44c3dfbac9440da876e7b3feaf1fc' == session, 'Did not get expected session ID'


class TestSessionEndCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.status_code = 401
        response.ok = False
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, 'bad session')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.status_code = 503
        response.ok = False
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogApiError):
            cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, '1234')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = dict(OK_RESPONSE)

        cmd = warthog.core.SessionEndCommand(transport, SCHEME_HOST, '1234')
        closed = cmd.send()
        assert closed, 'Did not get expected True result from session close'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeEnableCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.status_code = 401
        response.ok = False
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.status_code = 404
        response.ok = False
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_permissions(self, transport, response):
        response.text = ''
        response.status_code = 400
        response.ok = False
        response.json.return_value = dict(NO_PERMISSIONS)

        with pytest.raises(warthog.exceptions.WarthogPermissionError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'app1.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.status_code = 503
        response.ok = False
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogApiError):
            cmd = warthog.core.NodeEnableCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        result = dict(NODE_ALTER)
        result['server']['action'] = 'enable'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeEnableCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        got_enabled = cmd.send()
        assert got_enabled, 'Did not get get expected True result from node enable'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeDisableCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.status_code = 401
        response.ok = False
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.status_code = 404
        response.ok = False
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_no_permissions(self, transport, response):
        response.text = ''
        response.status_code = 400
        response.ok = False
        response.json.return_value = dict(NO_PERMISSIONS)

        with pytest.raises(warthog.exceptions.WarthogPermissionError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'app1.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.status_code = 503
        response.ok = False
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogApiError):
            cmd = warthog.core.NodeDisableCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.post.called, 'Expected transport ".post() to be called'

    def test_send_success(self, transport, response):
        result = dict(NODE_ALTER)
        result['server']['action'] = 'disable'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeDisableCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        got_disabled = cmd.send()
        assert got_disabled, 'Did not get get expected True result from node disable'
        assert transport.post.called, 'Expected transport ".post() to be called'


class TestNodeStatusCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.status_code = 401
        response.ok = False
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.status_code = 404
        response.ok = False
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.status_code = 503
        response.ok = False
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogApiError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_enabled(self, transport, response):
        result = dict(NODE_OPER)
        result['server']['oper']['state'] = 'Up'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_ENABLED == status, 'Did not get expected enabled status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_disabled(self, transport, response):
        result = dict(NODE_OPER)
        result['server']['oper']['state'] = 'Disabled'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_DISABLED == status, 'Did not get expected disabled status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_down(self, transport, response):
        result = dict(NODE_OPER)
        result['server']['oper']['state'] = 'Down'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeStatusCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        status = cmd.send()
        assert warthog.core.STATUS_DOWN == status, 'Did not get expected down status'
        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_server_no_known_status(self, transport, response):
        result = dict(NODE_OPER)
        result['server']['oper']['state'] = 'Shutdown'

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        with pytest.raises(warthog.exceptions.WarthogNodeStatusError):
            cmd = warthog.core.NodeStatusCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'


class TestNodeActiveConnectionsCommand(object):
    def test_send_invalid_session(self, transport, response):
        response.text = ''
        response.status_code = 401
        response.ok = False
        response.json.return_value = dict(INVALID_SESSION)

        with pytest.raises(warthog.exceptions.WarthogInvalidSessionError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_no_such_server(self, transport, response):
        response.text = ''
        response.status_code = 404
        response.ok = False
        response.json.return_value = dict(NO_SUCH_SERVER)

        with pytest.raises(warthog.exceptions.WarthogNoSuchNodeError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'bad.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_unknown_error(self, transport, response):
        response.text = ''
        response.status_code = 503
        response.ok = False
        response.json.return_value = dict(SOME_CRAZY_ERROR)

        with pytest.raises(warthog.exceptions.WarthogApiError):
            cmd = warthog.core.NodeActiveConnectionsCommand(
                transport, SCHEME_HOST, '1234', 'good.example.com')
            cmd.send()

        assert transport.get.called, 'Expected transport ".get() to be called'

    def test_send_success(self, transport, response):
        result = dict(NODE_STATS)
        result['server']['stats']['curr-conn'] = 42

        response.text = ''
        response.status_code = 200
        response.ok = True
        response.json.return_value = result

        cmd = warthog.core.NodeActiveConnectionsCommand(
            transport, SCHEME_HOST, '1234', 'good.example.com')
        connections = cmd.send()
        assert 42 == connections, 'Did not get expected active connections'
        assert transport.get.called, 'Expected transport ".get() to be called'
