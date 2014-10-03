# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function, division
import time

import warthog.core
import warthog.exc
import warthog.transport


class WarthogCommandFactory(object):
    def __init__(self, transport):
        self._transport = transport

    def get_session_start(self, scheme_host, username, password):
        return warthog.core.SessionStartCommand(
            self._transport, scheme_host, username, password)

    def get_session_end(self, scheme_host, session_id):
        return warthog.core.SessionEndCommand(
            self._transport, scheme_host, session_id)

    def get_server_status(self, scheme_host, session_id):
        return warthog.core.NodeStatusCommand \
            (self._transport, scheme_host, session_id)

    def get_enable_server(self, scheme_host, session_id):
        return warthog.core.NodeEnableCommand(
            self._transport, scheme_host, session_id)

    def get_disable_server(self, scheme_host, session_id):
        return warthog.core.NodeDisableCommand(
            self._transport, scheme_host, session_id)

    def get_active_connections(self, scheme_host, session_id):
        return warthog.core.NodeActiveConnectionsCommand(
            self._transport, scheme_host, session_id)


def get_default_cmd_factory():
    transport = warthog.transport.TransportBuilder() \
        .disable_verify() \
        .use_tlsv1() \
        .get()

    return WarthogCommandFactory(transport)


class _SessionManager(object):
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


def try_repeatedly(method, interval, max_retries):
    retries = 0

    while True:
        try:
            return method()
        except warthog.exc.WarthogError as e:
            if e.api_code not in warthog.core.TRANSIENT_ERRORS or retries >= max_retries:
                raise
            time.sleep(interval)
            retries += 1


class WarthogClient(object):
    _logger = warthog.core.get_log()
    _default_wait_interval = 2

    def __init__(self, scheme_host, username, password, wait_interval=_default_wait_interval, commands=None):
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._interval = wait_interval
        self._commands = commands if commands is not None else get_default_cmd_factory()

    def context(self):
        self._logger.debug('Creating new session context for %s', self._scheme_host)

        return _SessionManager(
            self._scheme_host, self._username, self._password, self._commands)

    def get_status(self, server):
        with self.context() as session:
            cmd = self._commands.get_server_status(self._scheme_host, session)
            return cmd.send(server)

    def disable_server(self, server, wait_for_connections=True, max_retries=5):
        with self.context() as session:
            disable = self._commands.get_disable_server(self._scheme_host, session)
            disable.send(server)

            if wait_for_connections:
                active = self._commands.get_active_connections(self._scheme_host, session)
                self._wait_for_connections(active, server, max_retries)

            status = self._commands.get_server_status(self._scheme_host, session)
            return warthog.core.STATUS_DISABLED == status.send(server)

    def _wait_for_connections(self, cmd, server, max_retries):
        retries = 0

        while retries < max_retries:
            conns = cmd.send(server)
            if conns == 0:
                break

            self._logger.debug(
                "Connections still active: %s, sleeping for %s seconds...", conns, self._interval)
            time.sleep(self._interval)
            retries += 1

    def enable_server(self, server, max_retries=5):
        with self.context() as session:
            cmd = self._commands.get_enable_server(self._scheme_host, session)
            method = lambda: cmd.send(server)

            # This function will only run the method once if max_retries is zero
            return try_repeatedly(method, self._interval, max_retries)


