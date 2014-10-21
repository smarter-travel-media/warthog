# -*- coding: utf-8 -*-

"""CLI interface for interacting with a load balancer using the Warthog client.

.. versionadded:: 0.4.0
"""

from __future__ import print_function, division

import sys
import collections

import codecs
import os
import os.path
import click
from .six.moves import configparser
import warthog
import warthog.api
import warthog.exceptions


# List of locations (from most preferred to least preferred) that will
# be searched for a configuration file if the location is not specified
# as an option.
DEFAULT_CONFIG_LOCATIONS = [
    os.path.join('/etc', 'warthog', 'warthog.ini'),
    os.path.join('/etc', 'warthog.ini'),
    os.path.join(sys.prefix, 'etc', 'warthog', 'warthog.ini'),
    os.path.join(sys.prefix, 'etc', 'warthog.ini'),
    os.path.join(os.path.expanduser('~'), '.warthog.ini'),
    os.path.join(os.getcwd(), 'warthog.ini')
]

# Simple struct to hold configuration information for a WarthogClient
ClientConfig = collections.namedtuple(
    'ClientConfig', ['scheme_host', 'username', 'password', 'verify'])


def get_config_location(option):
    """Get the location of the configuration file to load.

    If the file passed as a command line argument is non-None it will
    be preferred over any of the default locations. Otherwise, each default
    location will be checked to see of the configuration file exists. If
    there are no configuration files available, return None.

    :param basestring option: Possibly ``None`` path to a configuration file
    :return: The location of the configuration file that should be loaded
        or ``None``
    :rtype: basestring
    """
    if option is not None:
        return option

    for location in DEFAULT_CONFIG_LOCATIONS:
        if os.path.exists(location):
            return location

    return None


def get_parser(location):
    """Attempt to create an INI file configuration parser that will load
    settings from the given location.

    Note that the configuration file will be opened assuming a UTF-8 encoding.

    :param basestring location: Path to a configuration file to open
    :return: Configuration parser to load the Warthog configuration from
    :rtype: configparser.SafeConfigParser
    :raises RuntimeError: If the location of the config file was ``None`` or
        if the file did not exist or could not be opened.
    """
    if location is None:
        raise RuntimeError(
            "No configuration file location was specified and none of "
            "the default locations checked were valid configuration files ("
            "{0} were checked).".format(', '.join(DEFAULT_CONFIG_LOCATIONS)))

    parser = configparser.SafeConfigParser()

    try:
        parser.readfp(codecs.open(location, 'r', encoding='utf-8'))
    except IOError:
        raise RuntimeError(
            "Configuration settings couldn't be read from {0}. Please make "
            "sure the file exists and is readable by the current user.".format(
                location))

    return parser


def parse_config(parser):
    """Use the given INI parser to build a struct of configuration values for
    the WarthogClient. Raise a BadParameter error if there are any missing values
    or the config file is malformed.

    :param configparser.SafeConfigParser parser: Parser to use for config values
    :return: Struct of settings for the client
    :rtype: ClientConfig
    :raises click.BadParameter: If the config file is malformed or any values are
        missing.
    """
    try:
        # Load all required configuration params and raise a BadParameter
        # error if any of them are missing or if the configuration file is
        # missing the 'warthog' section.
        scheme_host = parser.get('warthog', 'scheme_host')
        username = parser.get('warthog', 'username')
        password = parser.get('warthog', 'password')
        verify = parser.getboolean('warthog', 'verify')
    except configparser.NoSectionError as e:
        raise click.BadParameter(
            "The configuration file seems to be missing a '{0}' section. Please "
            "make sure this section exists and re-run this command.".format(e.section))
    except configparser.NoOptionError as e:
        raise click.BadParameter(
            "The configuration file seems to be missing the '{0}' option. Please "
            "make sure this option exists and re-run this command.".format(e.option))

    return ClientConfig(
        scheme_host=scheme_host,
        username=username,
        password=password,
        verify=verify)


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

    config_file = get_config_location(config)
    try:
        # There was some problem opening the configuration file (doesn't
        # exist or maybe we can't read it). Blame the user, they should have
        # done something to prevent this. Why does everything have to be
        # our responsibility?
        parser = get_parser(config_file)
    except RuntimeError as e:
        raise click.BadParameter(str(e))

    values = parse_config(parser)

    factory = None
    if not values.verify:
        # We only need a custom command factory if we've chosen not to
        # verify certificates (since verifying them is the default). Note
        # we don't allow the SSL version to be overridden. Doing so would
        # be a little messy trying to parse so just don't do it.
        transport = warthog.api.get_transport_factory(verify=False)
        factory = warthog.api.CommandFactory(transport)

    ctx.obj = warthog.api.WarthogClient(values.scheme_host, values.username, values.password, commands=factory)


@click.command()
@click.argument('server')
@click.pass_context
def enable(ctx, server):
    """Enable a server by hostname."""
    try:
        if not ctx.obj.enable_server(server):
            click.echo('{0} could not be enabled'.format(server))
            ctx.exit(1)
    except warthog.exceptions.WarthogNoSuchNodeError:
        raise click.BadParameter("{0} doesn't appear to be a known node".format(server))


@click.command()
@click.argument('server')
@click.pass_context
def disable(ctx, server):
    """Disable a server by hostname."""
    try:
        if not ctx.obj.disable_server(server):
            click.echo('{0} could not be disabled'.format(server))
            ctx.exit(1)
    except warthog.exceptions.WarthogNoSuchNodeError:
        raise click.BadParameter("{0} doesn't appear to be a known node".format(server))


@click.command()
@click.argument('server')
@click.pass_context
def status(ctx, server):
    """Get the status of a server by hostname."""
    try:
        click.echo(ctx.obj.get_status(server))
    except warthog.exceptions.WarthogNoSuchNodeError:
        raise click.BadParameter("{0} doesn't appear to be a known node".format(server))


@click.command()
@click.argument('server')
@click.pass_context
def connections(ctx, server):
    """Get active connections to a server by hostname."""
    try:
        click.echo(ctx.obj.get_connections(server))
    except warthog.exceptions.WarthogNoSuchNodeError:
        raise click.BadParameter("{0} doesn't appear to be a known node".format(server))


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
    click.echo(os.linesep.join(DEFAULT_CONFIG_LOCATIONS))


main.add_command(enable)
main.add_command(disable)
main.add_command(status)
main.add_command(connections)
main.add_command(default_config)
main.add_command(config_path)
