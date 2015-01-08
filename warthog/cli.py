# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2015 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.cli
~~~~~~~~~~~

CLI interface for interacting with a load balancer using the Warthog client.
"""
import functools

import os

import os.path
import click
import warthog
import warthog.api
from .packages import six
import requests


def error_wrapper(func):
    """Decorator that coverts possible errors raised by the WarthogClient
    into instances of ClickExceptions so that they may be rendered automatically
    """

    # pylint: disable=missing-docstring
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except warthog.api.WarthogNoSuchNodeError as e:
            raise click.BadParameter("{0} doesn't appear to be a known node".format(e.server))
        except warthog.api.WarthogAuthFailureError as e:
            raise click.ClickException(
                "Authentication with the load balancer failed. The error was: {0}".format(e))
        except requests.ConnectionError as e:
            raise click.ClickException(
                "Connecting to the load balancer failed. The error was {0}".format(e))

    return wrapper


class WarthogClientFacade(object):
    """Wrapper around a :class:`warthog.client.WarthogClient` that coverts
    exceptions encountered into exceptions that click will handle automatically.
    """

    def __init__(self, client):
        self._client = client

    # pylint: disable=missing-docstring
    @error_wrapper
    def get_status(self, *args, **kwargs):
        return self._client.get_status(*args, **kwargs)

    # pylint: disable=missing-docstring
    @error_wrapper
    def get_connections(self, *args, **kwargs):
        return self._client.get_connections(*args, **kwargs)

    # pylint: disable=missing-docstring
    @error_wrapper
    def disable_server(self, *args, **kwargs):
        return self._client.disable_server(*args, **kwargs)

    # pylint: disable=missing-docstring
    @error_wrapper
    def enable_server(self, *args, **kwargs):
        return self._client.enable_server(*args, **kwargs)


@click.group()
@click.help_option('--help')
@click.version_option(version=warthog.__version__)
@click.option('--config', help='Path to a configuration file to use for the load balancer API', type=click.Path())
@click.pass_context
def main(ctx, config):
    """Interact with a load balancer using the Warthog client."""
    # Don't try to load config files or bootstrap the client if we're
    # just running the command to dump a default configuration file for
    # someone to customize or printing the config search path.
    if ctx.invoked_subcommand in ('default-config', 'config-path'):
        return

    # Passing the config file unconditionally here since if the user hasn't
    # specified one it'll be None and the config loader will use the default
    # locations.
    loader = warthog.api.WarthogConfigLoader(config_file=config)

    try:
        # Expected errors that might be raised during parsing. These will
        # already have nice user-facing messages so we just reraise them as
        # BadParameter exceptions with the same message.
        loader.initialize()
    except warthog.api.WarthogConfigError as e:
        raise click.ClickException(six.text_type(e))

    settings = loader.get_settings()
    factory = None

    if not settings.verify:
        # We only need a custom command factory if we've chosen not to
        # verify certificates (since verifying them is the default). Note
        # we don't allow the SSL version to be overridden. Doing so would
        # be a little messy trying to parse so just don't do it.
        transport = warthog.api.get_transport_factory(verify=False)
        factory = warthog.api.CommandFactory(transport)

    # Wrap the client in a facade that translates expected errors into
    # exceptions that click will render as error messages for the user.
    ctx.obj = WarthogClientFacade(warthog.api.WarthogClient(
        settings.scheme_host,
        settings.username,
        settings.password,
        commands=factory))


@click.command()
@click.argument('server')
@click.pass_context
def enable(ctx, server):
    """Enable a server by hostname."""
    if not ctx.obj.enable_server(server):
        click.echo('{0} could not be enabled'.format(server))
        ctx.exit(1)


@click.command()
@click.argument('server')
@click.pass_context
def disable(ctx, server):
    """Disable a server by hostname."""
    if not ctx.obj.disable_server(server):
        click.echo('{0} could not be disabled'.format(server))
        ctx.exit(1)


@click.command()
@click.argument('server')
@click.pass_context
def status(ctx, server):
    """Get the status of a server by hostname."""
    click.echo(ctx.obj.get_status(server))


@click.command()
@click.argument('server')
@click.pass_context
def connections(ctx, server):
    """Get active connections to a server by hostname."""
    click.echo(ctx.obj.get_connections(server))


@click.command('default-config')
def default_config():
    """Print a default configuration file."""
    click.echo(os.linesep.join([
        '[warthog]',
        'scheme_host = https://lb.example.com',
        'username = username',
        'password = password',
        'verify = yes'
    ]))


@click.command('config-path')
def config_path():
    """Print the config file search PATH."""
    click.echo(os.linesep.join(warthog.api.DEFAULT_CONFIG_LOCATIONS))


main.add_command(enable)
main.add_command(disable)
main.add_command(status)
main.add_command(connections)
main.add_command(default_config)
main.add_command(config_path)
