# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function, division
import time

import warthog.core


class CommandFactory(object):
    def get_session_start(self, scheme_host, username, password):
        return warthog.core.SessionStartCommand(scheme_host, username, password)

    def get_session_end(self, scheme_host, session_id):
        return warthog.core.SessionEndCommand(scheme_host, session_id)

    def get_server_status(self, scheme_host, session_id):
        return warthog.core.NodeStatusCommand(scheme_host, session_id)

    def get_enable_server(self, scheme_host, session_id):
        return warthog.core.NodeEnableCommand(scheme_host, session_id)

    def get_disable_server(self, scheme_host, session_id):
        return warthog.core.NodeDisableCommand(scheme_host, session_id)

    def get_active_connections(self, scheme_host, session_id):
        return warthog.core.NodeActiveConnectionsCommand(scheme_host, session_id)


class SessionManager(object):
    def __init__(self, scheme_host, username, password, commands):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._commands = commands
        self._session = None

    def __enter__(self):
        start_cmd = self._commands.get_session_start(
            self._scheme_host, self._username, self._password)
        self._session = start_cmd.send()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_cmd = self._commands.get_session_end(
            self._scheme_host, self._session)
        end_cmd.send()
        self._session = None
        return False


class WarthogClient(object):
    def __init__(self, scheme_host, username, password, commands=None):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._commands = commands if commands is not None else CommandFactory()

    def context(self):
        return SessionManager(
            self._scheme_host, self._username, self._password, self._commands)

    def get_status(self, server):
        with self.context() as session:
            cmd = self._commands.get_server_status(self._scheme_host, session)
            return cmd.send(server)

    def disable_server(self, server, wait_for_connections=True, max_wait_secs=10):
        with self.context() as session:
            disable = self._commands.get_disable_server(self._scheme_host, session)
            disable.send(server)

            if wait_for_connections:
                self._wait_for_active_connections(session, server, max_wait_secs)

            status = self._commands.get_server_status(self._scheme_host, session)
            return warthog.core.STATUS_DISABLED == status.send(server)

    def _wait_for_active_connections(self, session, server, max_wait_secs):
        interval = 2
        elapsed = 0
        while elapsed < max_wait_secs:
            active = self._commands.get_active_connections(self._scheme_host, session)
            conns = active.send(server)

            if conns == 0:
                break

            time.sleep(interval)
            elapsed += interval

    def enable_server(self, server):
        with self.context() as session:
            cmd = self._commands.get_enable_server(self._scheme_host, session)
            return cmd.send(server)


