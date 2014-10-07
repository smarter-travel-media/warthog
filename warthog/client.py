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
        """Get a new command instance to start a session.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring username: Name of the user to authenticate with.
        :param basestring password: Password for the user to authenticate with.
        :return: A new command to start a session.
        :rtype: warthog.core.SessionStartCommand
        """
        return warthog.core.SessionStartCommand(
            self._transport_factory(), scheme_host, username, password)

    def get_session_end(self, scheme_host, session_id):
        """Get a new command instance to close an existing session.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring session_id: Previously authenticated session ID.
        :return: A new command to close a session.
        :rtype: warthog.core.SessionEndCommand
        """
        return warthog.core.SessionEndCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_server_status(self, scheme_host, session_id):
        """Get a new command to get the status (enabled / disabled) of a server.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring session_id: Previously authenticated session ID.
        :return: A new command to get the status of a server.
        :rtype: warthog.core.NodeStatusCommand
        """
        return warthog.core.NodeStatusCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_enable_server(self, scheme_host, session_id):
        """Get a new command to enable a server at the node level.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring session_id: Previously authenticated session ID.
        :return: A new command to enable a server.
        :rtype: warthog.core.NodeEnableCommand
        """
        return warthog.core.NodeEnableCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_disable_server(self, scheme_host, session_id):
        """Get a new command to disable a server at the node level.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring session_id: Previously authenticated session ID.
        :return: A new command to disable a server.
        :rtype: warthog.core.NodeDisableCommand
        """
        return warthog.core.NodeDisableCommand(
            self._transport_factory(), scheme_host, session_id)

    def get_active_connections(self, scheme_host, session_id):
        """Get a new command to get the number of active connections to a server.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring session_id: Previously authenticated session ID.
        :return: A new command to get active connections to a server.
        :rtype: warthog.core.NodeActiveConnectionsCommand
        """
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
        """Set the load balancer scheme/host/port combination, username, password, and
        command factory to use for starting and ending sessions with the load balancer.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring username: Name of the user to authenticate with.
        :param basestring password: Password for the user to authenticate with.
        :param WarthogCommandFactory commands: Factory instance for creating new commands
            for starting and ending sessions with the load balancer.
        """
        self._scheme_host = scheme_host
        self._username = username
        self._password = password
        self._commands = commands
        self._session = None

    def __enter__(self):
        """Establish a new session with the load balancer and return the generated
        session ID when entering this context.

        :return: Authenticated session ID
        :rtype: unicode
        :raises warthog.exceptions.WarthogAuthFailureError: If the authentication
            failed for some reason.
        """
        start_cmd = self._commands.get_session_start(
            self._scheme_host, self._username, self._password)
        self._session = start_cmd.send()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the current session, making sure not to suppress any exceptions generated
        within the block we are exiting.

        :return: False, always
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
        """Set the load balancer scheme/host/port combination, username and password
        to use for connecting and authenticating with the load balancer.

        Optionally, the amount of time to wait between retries of various operations
        and the factory used for creating commands may be set.

        If the interval between retries is not supplied, the default is two seconds.

        If the command factory is not supplied, a default instance will be used. The
        command factory is also responsible for creating new :class:`requests.Session`
        instances to be used by each command. The default configuration is to use
        session instances that use TLSv1 for SSL connections and verify certificates.

        :param basestring scheme_host: Scheme, host, and port combination of the load balancer.
        :param basestring username: Name of the user to authenticate with.
        :param basestring password: Password for the user to authenticate with.
        :param int wait_interval: How long (in seconds) to wait between each retry of
            various operations (waiting for nodes to transition, waiting for connections
            to close, etc.).
        :param WarthogCommandFactory commands: Factory instance for creating new commands
            for starting and ending sessions with the load balancer.
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
        :data:`warthog.core.STATUS_DISABLED`, :data:`warthog.core.STATUS_DOWN`.

        :param basestring server: Hostname of the server to get the status of.
        :return: The current status of the server, enabled or disabled.
        :rtype: basestring
        :raises warthog.exceptions.WarthogAuthFailureError: If authentication with
            the load balancer failed when trying to establish a new session for this
            operation.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the load balancer does
            not recognize the given hostname.
        :raises warthog.exceptions.WarthogNodeStatusError: If there are any other
            problems getting the status of the given server.
        """
        with self._context() as session:
            cmd = self._commands.get_server_status(self._scheme_host, session)
            return cmd.send(server)

    def disable_server(self, server, max_retries=5):
        """Disable a server at the node level, optionally retrying when there are transient
        errors and waiting for the number of active connections to the server to reach zero.

        If ``max_retries`` is zero, no attempt will be made to retry on transient errors
        or to wait until there are no active connections to the server, the method will
        return immediately.

        :param basestring server: Hostname of the server to disable
        :param int max_retries: Max number of times to sleep and retry when encountering
            some sort of transient error when disabling the server and while waiting for
            the number of active connections to a server to reach zero.
        :return: True if the server was disabled, false otherwise.
        :rtype: bool
        :raises warthog.exceptions.WarthogAuthFailureError: If authentication with
            the load balancer failed when trying to establish a new session for this
            operation.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the load balancer does
            not recognize the given hostname.
        :raises warthog.exceptions.WarthogNodeDisableError: If there are any other
            problems disabling the given server.
        """
        with self._context() as session:
            disable = self._commands.get_disable_server(self._scheme_host, session)
            self._try_repeatedly(lambda: disable.send(server), max_retries)

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
        """Enable a server at the node level, optionally retrying when there are transient
        errors and waiting for the server to enter the expected, enabled state.

        If ``max_retries`` is zero, no attempt will be made to retry on transient errors
        or to wait until the server enters the expected, enabled state, the method will
        return immediately.

        :param basestring server: Hostname of the server to enable
        :param int max_retries: Max number of times to sleep and retry when encountering
            some transient error while trying to enable the server
        :return: True if the server was enabled, false otherwise
        :rtype: bool
        :raises warthog.exceptions.WarthogAuthFailureError: If authentication with
            the load balancer failed when trying to establish a new session for this
            operation.
        :raises warthog.exceptions.WarthogNoSuchNodeError: If the load balancer does
            not recognize the given hostname.
        :raises warthog.exceptions.WarthogNodeEnableError: If there are any other
            problems enabling the given server.
        """
        with self._context() as session:
            enable = self._commands.get_enable_server(self._scheme_host, session)
            self._try_repeatedly(lambda: enable.send(server), max_retries)

            status = self._commands.get_server_status(self._scheme_host, session)
            self._wait_for_enable(status, server, max_retries)

            return warthog.core.STATUS_ENABLED == status.send(server)

    def _wait_for_enable(self, cmd, server, max_retries):
        retries = 0

        while retries < max_retries:
            status = cmd.send(server)
            if status == warthog.core.STATUS_ENABLED:
                break

            self._logger.debug(
                "Server is not yet enabled (%s), sleeping for %s seconds...", status, self._interval)
            time.sleep(self._interval)
            retries += 1

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


