CLI Tool
========

Since version :doc:`0.4.0 </changes>` Warthog includes a CLI client for using
to interact with a load balancer in addition to the library client. The CLI client
supports most of the same operations as the :class:`warthog.client.WarthogClient`
class. The CLI client has the advantage of working from any type of deploy process,
not just Python ones.

Configuration and usage of the CLI client is described below.


Usage
-----

Usage of the Warthog CLI client is based on running various commands. Commands
are specified as arguments to the ``warthog`` program. Some of the commands take
additional arguments or options. The most basic usage looks like the following.

.. code-block:: bash

    $ warthog default-config

In the example above, we run the ``default-config`` command with no options or
arguments. The ``default-config`` simply prints an example configuration file
for the client.

A slightly more involved example might involve passing an argument or option
to the command. The example below explores this.

.. code-block:: bash

    $ warthog status --help


The this example passes the ``--help`` option to the ``status`` command. This causes
the Warthog CLI client to print out the details on using the ``status`` command.

.. code-block:: bash

    $ warthog status app1.example.com

This example passes the argument ``app1.example.com`` to the ``status`` command.
In this case, the CLI client prints the status of ``app1.example.com`` (something
like ``enabled`` or ``disabled``).

Command-line Options
--------------------

The following options are supported by the root ``warthog`` script. For more
information about a specific command, use the ``--help`` option with that command.

.. cmdoption:: --help

    Display basic usage information about the Warthog CLI client and exit.

.. cmdoption:: --version

    Display the version of Warthog and exit.

.. cmdoption:: --config <file>

    Set an explicit path to the configuration file for the Warthog CLI client
    instead of relying on the multiple default locations that are searched. If
    this option is specified all other potential locations for files are ignored.

Commands
--------

.. cmdoption:: status <server>

    Get the status of the given server (by host name). The status will be one of
    ``enabled``, ``disabled``, or ``down``. If the server is not in any load balancer
    pools an error message will be displayed instead and the exit code will be
    non-zero.

.. cmdoption:: connections <server>

    Get the number of active connections to the given server (by host name). The
    number of active connections will be an integer greater than or equal to zero.
    If the server is not in any load balancer pools an error message will be
    displayed instead and the exit code will be non-zero.

.. cmdoption:: disable <server>

    Disable the given server (by host name). The CLI client will wait until the
    number of active connections to the server reaches zero before returning. If
    the server is not in any load balancer pools or was not able to be disabled
    before the CLI client gave up waiting an error message will be displayed and
    the exit code will be non-zero. The number of retries attempted is governed
    by the default value in :meth:`warthog.client.WarthogClient.disable_server`.

.. cmdoption:: enable <server>

    Disable the given server (by host name). The CLI client will wait until the
    the server enters the ``enabled`` state. If the server is not in any load
    balancer pools or did not enter the ``enabled`` state before the CLI client
    gaven up waiting an error message will be displayed and the exit code will
    be non-zero. The number of retires attempted is governed by the default
    value in :meth:`warthog.client.WarthogClient.enable_server`.


.. cmdoption:: default-config

    Print the contents of an example INI-style configuration file for the Warthog
    CLI client. The output from this command can be piped into a file and then
    edited for your particular load balancer host and credentials.

.. cmdoption:: config-path

    Print (one path per line) each of the various locations that a configuration
    file will be searched for if not specified with the ``--config`` option.


Configuration
-------------

Up till now we've mentioned that the Warthog CLI client uses a configuration file but
we haven't really gotten into what exactly that configuration file is or what it looks
like. Let's go over that now.

In order to interact with your load balancer over the HTTP or HTTPS API, the Warthog
client needs a few pieces of information.

* The scheme, host (or IP), and port that it should use for talking to the load balancer.
* The username it should use for authentication with the load balancer.
* The password associated with the username it should use.
* Whether or not SSL certificates should be validated (similar to how your browser validates
  them).

Syntax
~~~~~~

The Warthog CLI client uses an INI-style_ configuration file. The format is shown below.

.. code-block:: ini

    [warthog]
    scheme_host = https://lb.example.com
    username = username
    password = password
    verify = yes

.. tabularcolumns:: |l|l|

========================= =======================================================================
``scheme_host``           Combination of scheme (either 'http' or 'https'), host name (or IP),
                          and port number. This is used to connect to the load balancer. Some
                          examples of valid values: ``http://10.1.2.3:8080``,
                          ``https://10.1.2.3:8443``, ``https://lb.example.com:8443``, or
                          ``http://lb.example.com``.

``username``              The username to use for authentication with the load balancer. Some
                          examples of valid values: ``admin``, ``deploy``, ``svc``.

``password``              Password to use along with the username for authentication with the
                          load balancer.

``verify``                If connecting to the load balancer over HTTPS, boolean to indicate if
                          the SSL certificate should be validated. This may be any boolean value
                          recognized by the Python INI parser_. Examples of valid true values
                          include ``1``, ``yes``, ``true``, and ``on``. Examples of valid false
                          values include ``0``, ``no``, ``false``, and ``off``.
========================= =======================================================================


.. _INI-style: http://en.wikipedia.org/wiki/INI_file
.. _parser: https://docs.python.org/2/library/configparser.html#ConfigParser.RawConfigParser.getboolean

Location
~~~~~~~~

If the ``--config`` option is not given the the Warthog CLI client, several locations will
be checked for a configuration file to use. The logic for deciding which locations to check
is described below. The locations will be checked in order until one that exists is found.

.. note::

    Searching for a configuration file will stop after the first one that exists, NOT the
    first one that can be read and contains valid values.

#. ``/etc/warthog/warthog.ini``
#. ``/etc/warthog.ini``
#. ``$PREFIX/etc/warthog/warthog.ini`` where $PREFIX is the value of :data:`sys.prefix` in Python
#. ``$PREFIX/etc/warthog.ini`` where $PREFIX is the value of :data:`sys.prefix` in Python
#. ``$HOME/.warthog.ini`` where $HOME is the home directory of the user running the script
#. ``$CWD/warthog.ini`` where $CWD is the current working directory when the script is run

If none of these paths exist and the ``--config`` option is not given, the CLI client will
abort.
