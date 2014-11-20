# -*- coding: utf-8 -*-
#
# Warthog - Simple client for A10 load balancers
#
# Copyright 2014 Smarter Travel
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
import sys

import codecs
import os.path
from .six import reraise
# pylint: disable=import-error
from .six.moves import configparser

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
    'WarthogConfigSettings', ['scheme_host', 'username', 'password', 'verify'])


class WarthogConfigLoader(object):
    """Load and parse configuration from an INI-style WarthogClient configuration file.

    If a specific configuration file is given during construction, this file will
    be used instead of checking the multiple possible default locations for configuration
    files. The default locations to be checked are an ordered list of paths contained
    in :data:`DEFAULT_CONFIG_LOCATIONS`.

    If a INI configuration parser instance is given during construction, this instance
    will be used to load and parse the configuration file. If not given, an instance
    of a :class:`configparser.SafeConfigParser` from the standard library will be used.

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
        been split into the .initialize() and .get_settings() methods. Additionally,
        loading and access of configuration settings is now thread safe.
    """

    def __init__(self, config_file=None, config_parser=None, encoding=DEFAULT_CONFIG_ENCODING):
        """Optionally, set a specific configuration file, parser for the file, and
        the encoding of the file.

        By default, multiple locations will be checked for a configuration file, an INI
        configuration parser from the standard library will be used, and the file is
        assumed to use UTF-8 encoding.

        :param basestring config_file: Optional explicit path to a configuration file
            to use.
        :param configparser.RawConfigParser config_parser: Optional configuration parser
            instance to use for reading and parsing a configuration file instead of
            the default parser (one of the INI parser from the standard library).
        :param basestring encoding: Encoding to use for reading the configuration file.
            Default is UTF-8
        """
        self._config_file = config_file
        self._config_parser = config_parser
        self._encoding = encoding
        self._lock = threading.RLock()
        self._settings = None

    # pylint: disable=missing-docstring
    def _get_config_file(self):
        if self._config_file is not None:
            return self._config_file

        for location in DEFAULT_CONFIG_LOCATIONS:
            if os.path.exists(location):
                return location

        return None

    # pylint: disable=missing-docstring
    def _get_config_parser(self):
        if self._config_parser is not None:
            return self._config_parser
        return configparser.SafeConfigParser()

    # pylint: disable=missing-docstring
    def _parse_config_file(self):
        config_file = self._get_config_file()
        config_parser = self._get_config_parser()

        if config_file is None:
            raise ValueError(
                "No configuration file was specified. Please set a "
                "configuration file or ensure that a configuration "
                "file exists in one of the default locations checked.")

        try:
            with codecs.open(config_file, 'r', encoding=self._encoding) as handle:
                config_parser.readfp(handle)
        except IOError as e:
            # Use reraise here to create a new IOError instance with a more helpful
            # error message but preserve the traceback of the original error that
            # was raised.
            reraise(
                IOError,
                IOError(
                    "The configuration file does not exist or could not read. "
                    "Please make sure {0} exists and can be read by the current "
                    "user. Original error message: {1}".format(config_file, e)),
                sys.exc_info()[2])

        try:
            scheme_host = config_parser.get('warthog', 'scheme_host')
            username = config_parser.get('warthog', 'username')
            password = config_parser.get('warthog', 'password')
            verify = config_parser.getboolean('warthog', 'verify')
        except configparser.NoSectionError as e:
            raise RuntimeError(
                "The configuration file seems to be missing a '{0}' section. Please "
                "make sure this section exists.".format(e.section))
        except configparser.NoOptionError as e:
            raise RuntimeError(
                "The configuration file seems to be missing the '{0}' option. Please "
                "make sure this option exists.".format(e.option))

        return WarthogConfigSettings(
            scheme_host=scheme_host,
            username=username,
            password=password,
            verify=verify)

    def initialize(self):
        """Load and parse a configuration an INI-style configuration file.

        The values parsed will be stored as a :class:`WarthogClientConfig` instance that
        may be accessed with the :meth:`get_settings` method.

        .. versionadded:: 0.6.0

        :return: Fluent interface
        :rtype: WarthogConfigLoader
        :raises ValueError: If no explicit configuration file was given and there were no
            configuration files in any of the default locations checked.
        :raises IOError: If the configuration file could not be opened or read for some
            reason.
        :raises RuntimeError: If the configuration file was malformed such has missing the
            required 'warthog' section or any of the expected values. See the :doc:`cli`
            section for more information about the expected configuration settings.
        """
        with self._lock:
            self._settings = self._parse_config_file()
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
                    "settings can be used (via the .initialize() method")
            return self._settings
