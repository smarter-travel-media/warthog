# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function, division

import pytest
import mock
import warthog.client
import warthog.core


SCHEME_HOST = 'https://lb.example.com'


class TestSessionContext(object):
    def setup(self):
        self.start_cmd = mock.Mock(spec=warthog.core.SessionStartCommand)
        self.end_cmd = mock.Mock(spec=warthog.core.SessionEndCommand)
        self.commands = mock.Mock(spec=warthog.client.CommandFactory)
        self.commands.get_session_start.return_value = self.start_cmd
        self.commands.get_session_end.return_value = self.end_cmd

    def test_enter_yields_session(self):
        self.start_cmd.send.return_value = '1234'

        context = warthog.client.SessionContext(SCHEME_HOST, 'user', 'password', self.commands)
        session = context.__enter__()

        assert '1234' == session, 'Did not get expected session ID'
        self.commands.get_session_start.assert_called_once_with(SCHEME_HOST, 'user', 'password')
        assert self.start_cmd.send.called, 'Expected session start .send() to be called'

    def test_exit_closes_previous_session(self):
        self.start_cmd.send.return_value = '1234'

        context = warthog.client.SessionContext(SCHEME_HOST, 'user', 'password', self.commands)
        context.__enter__()
        context.__exit__(None, None, None)

        self.commands.get_session_end.assert_called_once_with(SCHEME_HOST, '1234')
        assert self.end_cmd.send.called, 'Expected session end .send() to be called'

    def test_exception_in_context_propagated(self):
        self.start_cmd.send.return_value = '1234'
        context = warthog.client.SessionContext(SCHEME_HOST, 'user', 'password', self.commands)

        with pytest.raises(RuntimeError):
            with context:
                raise RuntimeError("AHH!")


class TestWarthogClient(object):
    pass
