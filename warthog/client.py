# -*- coding: utf-8 -*-
#
# Warthog - Client for A10 load balancers
#
# Copyright 2014 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.client
~~~~~~~~~~~~~~



"""

from __future__ import print_function, division
import time

import warthog.core
import warthog.exceptions
import warthog.transport


class WarthogCommandFactory(object):
    """Factory for getting new :mod:`warthog.core` command instances that each
    perform some type of request against the load balancer API.
    """

    def __init__(self, transport_factory):
        """Set the a factory that will create new HTTP Sessions instances to be
        used for executing commands.

        :param func transport_factory: Callable for creating new Session instances
            for executing commands.
        """
        self._transport_factory = transport_factory

    def get_session_start(self, scheme_host, username, password):
        return warthog.core.SessionStartCommand(
            self._transport_factory(), scheme_host, username, password)

    def get_session_end(self, scheme_host, session_id):
        return warthog.core.SessionEndCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_server_status(self, scheme_host, session_id):
        return warthog.core.NodeStatusCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_enable_server(self, scheme_host, session_id):
        return warthog.core.NodeEnableCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_disable_server(self, scheme_host, session_id):
        return warthog.core.NodeDisableCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_active_connections(self, scheme_host, session_id):
        return warthog.core.NodeActiveConnectionsCommand(
            self._transport_factory(), scheme_host, session_id)


def _get_default_cmd_factory():
    """Get a :class:`WarthogCommandFactory` instance configured to use the
    TLS version expected by the A10 when using https connections.

    :return: Default command factory for building new commands to interact
        with the A10 load balancer
    :rtype: WarthogCommandFactory
    """
    return WarthogCommandFactory(warthog.transport.get_factory())


class _SessionContext(object):
    """Context manager implementation that begins a new authenticated session
    with the load balancer when entering the context and cleans it up after
    exiting the context.

    This class is not thread safe.
    """

    def __init__(self, scheme_host, username, password, commands):
        """



        :param scheme_host:
        :param username:
        :param password:
        :param commands:
        """
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._commands = commands
        self._session = None

    def __enter__(self):
        """



        :return:
        """
        start_cmd = self._commands.get_session_start(
            self._scheme_host, self._username, self._password)
        self._session = start_cmd.send()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        :return:
        """
        end_cmd = self._commands.get_session_end(
            self._scheme_host, self._session)
        end_cmd.send()
        self._session = None
        return False


class WarthogClient(object):
    """Client for interacting with an A10 load balancer to get the status
    of nodes managed by it, enable them at the node level, and disable them
    at the node level.

    Note that all methods in this client that operate on servers work at the
    node level. That is, servers are disabled for all groups they are in or
    potentially enabled for all groups they are in. It may still be possible
    for a node to be disabled in some group but enabled at the node level.
    This client does not handle that case and assumes that it is the only
    mechanism being used to operate on nodes.

    In practice this should not be an issue since the primary use case of this
    client is to safely remove a node from the load balancer so that it may be
    deployed to. If a node remains disabled for some group after being enabled
    at the node level, so be it.

    This class is thread safe.
    """
    _logger = warthog.core.get_log()
    _default_wait_interval = 2

    def __init__(self, scheme_host, username, password, wait_interval=_default_wait_interval, commands=None):
        """




        :param scheme_host:
        :param username:
        :param password:
        :param wait_interval:
        :param commands:
        """
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._interval = wait_interval
        self._commands = commands if commands is not None else _get_default_cmd_factory()

    def _context(self):
        """Get a new :class:`_SessionContext` instance."""
        self._logger.debug('Creating new session context for %s', self._scheme_host)

        return _SessionContext(
            self._scheme_host, self._username, self._password, self._commands)

    def get_status(self, server):
        """Get the current status of the given server, at the node level.

        The status will be one of the constants :data:`warthog.core.STATUS_ENABLED`
        or :data:`warthog.core.STATUS_DISABLED`.

        :param basestring server: Hostname of the server to get the status of.
        :return: The current status of the server, enabled or disabled.
        :rtype: basestring
        :raises warthog.exceptions.WarthogAuthFailureError:
        :raises warthog.exceptions.WarthogNoSuchNodeError:
        :raises warthog.exceptions.WarthogNodeStatusError:
        """
        with self._context() as session:
            cmd = self._commands.get_server_status(self._scheme_host, session)
            return cmd.send(server)

    def disable_server(self, server, wait_for_connections=True, max_retries=5):
        """



        :param basestring server:
        :param bool wait_for_connections:
        :param int max_retries:
        :return:
        :rtype: bool
        :raises warthog.exceptions.WarthogAuthFailureError:
        :raises warthog.exceptions.WarthogNoSuchNodeError:
        :raises warthog.exceptions.WarthogNodeDisableError:
        """
        with self._context() as session:
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
        """



        :param server:
        :param max_retries:
        :return:
        :rtype: bool
        :raises warthog.exceptions.WarthogAuthFailureError:
        :raises warthog.exceptions.WarthogNoSuchNodeError:
        :raises warthog.exceptions.WarthogNodeEnableError:
        """
        with self._context() as session:
            cmd = self._commands.get_enable_server(self._scheme_host, session)
            method = lambda: cmd.send(server)

            # This function will only run the method once if max_retries is zero
            return self._try_repeatedly(method, max_retries)

    def _try_repeatedly(self, method, max_retries):
        """Execute a method, retrying if it fails due to a transient error
        up to a given number of times, with the instance-wide interval in
        between each try.
        """
        retries = 0

        while True:
            try:
                return method()
            except warthog.exceptions.WarthogError as e:
                if e.api_code not in warthog.core.TRANSIENT_ERRORS or retries >= max_retries:
                    raise
                self._logger.debug(
                    "Encountered transient error %s - %s, retrying... ", e.api_code, e.api_msg)
                time.sleep(self._interval)
                retries += 1


