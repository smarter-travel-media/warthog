# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014-2015 Smarter Travel
#
# Available under the MIT license. See LICENSE for details.
#

"""
warthog.config
~~~~~~~~~~~~~~

Load and parse configuration for a client from an INI-style file.
"""

import collections
import threading
import ssl
import sys

import codecs
import os.path
import warthog.exceptions
from .packages import six
# pylint: disable=import-error
from .packages.six.moves import configparser

# List of locations (from most preferred to least preferred) that will
# be searched for a configuration file. These locations are typically
# only searched when an explicit configuration file is not used.
DEFAULT_CONFIG_LOCATIONS = [
    os.path.join('/etc', 'warthog', 'warthog.ini'),
    os.path.join('/etc', 'warthog.ini'),
    os.path.join(sys.prefix, 'etc', 'warthog', 'warthog.ini'),
    os.path.join(sys.prefix, 'etc', 'warthog.ini'),
    os.path.join(os.path.expanduser('~'), '.warthog.ini'),
    os.path.join(os.getcwd(), 'warthog.ini')
]


# By default, we assume that the configuration file is in UTF-8 unless
# the caller indicates it is in some other encoding.
DEFAULT_CONFIG_ENCODING = 'utf-8'


# Simple immutable struct to hold configuration information for a WarthogClient
WarthogConfigSettings = collections.namedtuple(
    'WarthogConfigSettings', ['scheme_host', 'username', 'password', 'verify', 'ssl_version'])


class WarthogConfigLoader(object):
    """Load and parse configuration from an INI-style WarthogClient configuration file.

    If a specific configuration file is given during construction, this file will
    be used instead of checking the multiple possible default locations for configuration
    files. The default locations to be checked are an ordered list of paths contained
    in :data:`DEFAULT_CONFIG_LOCATIONS`.

    .. note::

        When checking for configuration files in default locations, each file will only
        be checked to see if it exists. It will not be checked to see if the file is
        readable or correctly formatted.

    This class is thread safe.

    .. versionadded:: 0.4.0

    .. versionchanged:: 0.6.0
        Loading, parsing, and access of configuration settings is now thread safe.

    .. versionchanged:: 0.6.0
        The .parse_configuration() method has been removed and the functionality has
        been split into the .initialize() and .get_settings() methods.

    .. versionchanged:: 0.10.0
        The :meth:`WarthogConfigLoader.__init__` method no longer directly takes a standard
        library INI parser as an option parameter, instead it now takes a WarthogConfigParser
        instance as an optional parameter.

    .. versionchanged:: 0.10.0
        See :doc:`changes` or :doc:`cli` for details about the changes to configuration
        file format.
    """

    def __init__(self, config_file=None, encoding=None, path_resolver=None, config_parser=None):
        """Optionally, set a specific configuration file, the encoding of the file, resolver
        to determine the configuration file to use, and custom configuration parser implementation.

        By default, multiple locations will be checked for a configuration file, the file
        is assumed to use UTF-8 encoding, and an

        :param str|unicode config_file: Optional explicit path to a configuration file
            to use.
        :param str|unicode encoding: Encoding to use for reading the configuration file.
            Default is UTF-8
        :param callable path_resolver: Callable that accepts a single argument (the explicit
            configuration file path to use) and determines what configuration file to use. It
            is typically only necessary to set this parameter for unit testing purposes.
        :param WarthogConfigParser config_parser: Optional configuration parser to use for
            reading and parsing the expected INI format for a Warthog configuration file. It
            is typically only necessary to set this parameter for unit testing purposes.
        """
        self._config_file = config_file
        self._encoding = encoding if encoding is not None else DEFAULT_CONFIG_ENCODING

        self._path_resolver = path_resolver if path_resolver is not None else \
            WarthogConfigFileResolver(DEFAULT_CONFIG_LOCATIONS)

        self._parser = config_parser if config_parser is not None else \
            WarthogConfigParser(configparser.SafeConfigParser())

        self._lock = threading.RLock()
        self._settings = None

    def initialize(self):
        """Load and parse a configuration an INI-style configuration file.

        The values parsed will be stored as a :class:`WarthogConfigSettings` instance that
        may be accessed with the :meth:`get_settings` method.

        .. versionadded:: 0.6.0

        .. versionchanged:: 0.8.0
            Errors locating or parsing configuration files now result in Warthog-specific
            exceptions (:class:`warthog.exceptions.WarthogConfigError`) instead of
            `ValueError`, `IOError`, or `RuntimeError`.

        :return: Fluent interface
        :rtype: WarthogConfigLoader
        :raises warthog.exceptions.WarthogNoConfigFileError: If no explicit configuration file
            was given and there were no configuration files in any of the default locations
            checked or if the configuration file could not be opened or read for some
            reason.
        :raises warthog.exceptions.WarthogMalformedConfigFileError: If the configuration
            file was malformed such has missing the required 'warthog' section or any of
            the expected values. See the :doc:`cli` section for more information about the
            expected configuration settings.
        """
        with self._lock:
            config_file, checked = self._path_resolver(self._config_file)
            self._settings = self._parser.parse(config_file, self._encoding, checked)
        return self

    def get_settings(self):
        """Get previously loaded and parsed configuration settings, raise an exception
        if the settings have not already been loaded and parsed.

        .. versionadded:: 0.6.0

        :return: Struct of configuration settings for the Warthog client
        :rtype: WarthogConfigSettings
        :raises RuntimeError: If a configuration file has not already been loaded and
            parsed.
        """
        with self._lock:
            if self._settings is None:
                raise RuntimeError(
                    "Configuration file must be loaded and parsed before "
                    "settings can be used (via the .initialize() method)")
            return self._settings


def parse_ssl_version(version_str, ssl_module=None):
    """Get the :mod:`ssl` protocol constant that represents the given version
    string if it exists, raising an error if the version string is malformed or
    does not correspond to a supported protocol.

    :param unicode version_str: Version string to resolve to a protocol
    :param module ssl_module: SSL module to get the protocol constant from
    :return: The ssl module protocol constant or ``None``
    :raises ValueError: If the version string did not match any known versions
        of SSL or TLS
    """
    if version_str is None:
        return None

    version_str = version_str.strip()
    if not version_str:
        return None

    ssl_module = ssl_module if ssl_module is not None else ssl

    # Get a list of all the 'PROTOCOL' constants in the SSL module, and
    # strip the 'PROTOCOL_' prefix. This is the set of supported SSL or
    # TLS versions that we'll compare the user input against.
    supported = set([const.replace('PROTOCOL_', '', 1) for const in dir(ssl_module)
                     if const.startswith('PROTOCOL_')])

    if version_str in supported:
        return getattr(ssl_module, 'PROTOCOL_' + version_str)

    raise ValueError(
        "Unsupported SSL/TLS version '" + version_str + "'. Supported: " + ', '.join(supported))


class WarthogConfigFileResolver(object):
    """Callable that returns a tuple of the form $path, $searched where
     $path is the configuration file that should be used or None (if there
     were no suitable files found) and $searched is a list of all paths that
     were checked to find a suitable file.

     If a configuration file was explicitly provided, it will be used without
     checking any of the default locations. If no file was explicitly provided
     each of the default locations will be checked to find one configuration
     file that exists.

     If no suitable file could be found, the callable will return the tuple
     ``None``, $searched where $searched is the list of locations checked.
    """

    def __init__(self, default_locations, exists_impl=None):
        self._default_locations = default_locations
        self._exists_impl = exists_impl if exists_impl is not None else os.path.exists

    def __call__(self, path):
        if path is not None:
            return path, [path]

        for default in self._default_locations:
            if self._exists_impl(default):
                return default, self._default_locations

        return None, self._default_locations


class WarthogConfigParser(object):
    """Facade for a standard library INI file parser that parses the expected
    configuration values for configuring a :class:`warthog.client.WarthogClient`
    instance.

    All configuration values are expected to be in the ``warthog`` section of
    the INI file. The ``ssl_version`` and ``verify`` values are not required, all
    others are.

    This class is not thread safe.
    """

    def __init__(self, parser_impl, open_impl=None):
        """Set the underlying standard library INI parser to use for reading
        Warthog configuration settings.

        :param configparser.RawConfigParser parser_impl: INI file parser to use
            for parsing Warthog configuration settings.
        :param callable open_impl: Open method for opening the configuration
            file. The method is expected to have the same signature as
            :func:`codes.open`. Callers should only need to supply this for unit
            testing purposes.
        """
        self._parser_impl = parser_impl
        self._open_impl = open_impl if open_impl is not None else codecs.open

    def _load_file(self, path, encoding, checked):
        """Open and load the configuration file at the given path."""
        if path is None:
            raise warthog.exceptions.WarthogNoConfigFileError(
                "No configuration file was specified. Please set a "
                "configuration file or ensure that a configuration "
                "file exists in one of the default locations checked",
                locations_checked=checked)

        try:
            with self._open_impl(path, 'r', encoding=encoding) as handle:
                self._parser_impl.readfp(handle)
        except IOError as e:
            six.reraise(
                warthog.exceptions.WarthogNoConfigFileError,
                warthog.exceptions.WarthogNoConfigFileError(
                    "The configuration file does not exist or could not read. "
                    "Please make sure {0} exists and can be read by the current "
                    "user. Original error message: {1}".format(path, e),
                    locations_checked=checked),
                sys.exc_info()[2])
        except UnicodeError as e:
            six.reraise(
                warthog.exceptions.WarthogMalformedConfigFileError,
                warthog.exceptions.WarthogMalformedConfigFileError(
                    "The configuration file {0} doesn't seem to be correctly encoded "
                    "{1} text. Please ensure that the file is valid text. Original "
                    "error message: {2}".format(path, encoding, e)),
                sys.exc_info()[2])

    def _get_ssl_version(self, section, option):
        """Get the specified TLS version in the config file or None."""
        if self._parser_impl.has_option(section, option):
            return parse_ssl_version(self._parser_impl.get(section, option))
        return None

    def _get_verify(self, section, option):
        """Get the certificate verify option in the config file or None."""
        if self._parser_impl.has_option(section, option):
            return self._parser_impl.getboolean(section, option)
        return None

    def _parse_file(self):
        """Parse the opened configuration file and return the results as a namedtuple."""
        try:
            scheme_host = self._parser_impl.get('warthog', 'scheme_host')
            username = self._parser_impl.get('warthog', 'username')
            password = self._parser_impl.get('warthog', 'password')
            verify = self._get_verify('warthog', 'verify')
            ssl_version = self._get_ssl_version('warthog', 'ssl_version')
        except configparser.NoSectionError as e:
            raise warthog.exceptions.WarthogMalformedConfigFileError(
                "The configuration file seems to be missing a '{0}' section. Please "
                "make sure this section exists".format(e.section), missing_section=e.section)
        except configparser.NoOptionError as e:
            raise warthog.exceptions.WarthogMalformedConfigFileError(
                "The configuration file seems to be missing the '{0}' option. Please "
                "make sure this option exists".format(e.option), missing_option=e.option)

        return WarthogConfigSettings(
            scheme_host=scheme_host,
            username=username,
            password=password,
            verify=verify,
            ssl_version=ssl_version)

    def parse(self, path, encoding, checked):
        """Attempt to open and parse the configuration file at the given
        path.

        :param str|unicode path: Path to the configuration file to parse.
        :param str|unicode encoding: Encoding to use when opening the file.
        :param list checked: List of the various locations checked before
            deciding on the configuration file to open.
        :return: The parsed configuration settings to use for creating a client.
        :rtype: WarthogConfigSettings
        """

        self._load_file(path, encoding, checked)
        return self._parse_file()
