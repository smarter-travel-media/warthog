Usage
=====

Some of the typical use cases for the Warthog library client are detailed below.

Usage During Deploy
-------------------

In the example below, we use the Warthog library client to disable each server in the
load balancer, install a new version of our project on it, restart our application, and
then enable the server in the load balancer.

.. code-block:: python

    from __future__ import print_function
    from warthog.api import WarthogClient

    MY_LB_HOST = 'https://lb.example.com'
    MY_LB_USER = 'deploy'
    MY_LB_PASS = 'Depl0yin47e!'

    HOSTS = ['app1.example.com', 'app2.example.com']

    def copy_my_project(host):
        pass

    def install_my_project(host):
        pass

    def restart_my_application(host):
        pass

    def install():
        client = WarthogClient(MY_LB_HOST, MY_LB_USER, MY_LB_PASS)

        for host in HOSTS:
            client.disable_server(host)

            copy_my_project(host)
            install_my_project(host)
            restart_my_application(host)

            client.enable_server(host)

        print('Installed project on all servers!')



Usage During Rolling Restart
----------------------------

In the example below, we use the Warthog library client to disable a server in the
load balancer while an application is restarted and then wait for the application to
become ready to serve requests.

.. code-block:: python

    from __future__ import print_function

    import time
    from warthog.api import WarthogClient

    MY_LB_HOST = 'https://lb.example.com'
    MY_LB_USER = 'deploy'
    MY_LB_PASS = 'Depl0yin47e!'

    HOSTS = ['app1.example.com', 'app2.example.com']

    def is_application_ready(host):
        pass

    def restart_my_application(host):
        pass

    def restart():
        client = WarthogClient(MY_LB_HOST, MY_LB_USER, MY_LB_PASS)

        for host in HOSTS:
            client.disable_server(host)

            restart_my_application(host):

            while not is_application_ready(host):
                time.sleep(5)

            client.enable_server(host)

        print('Application restarted on all servers!')

Usage as Context Manager
------------------------

In this example, we use the Warthog library client as a context manager that
will automatically disable a server, and then re-enable it after the context
exits.

.. note::

    When used as a context manager, the node will only be re-enabled if it
    was enabled before we entered the context.

.. code-block:: python

    from __future__ import print_function

    import time
    from warthog.api import WarthogClient

    MY_LB_HOST = 'https://lb.example.com'
    MY_LB_USER = 'deploy'
    MY_LB_PASS = 'Depl0yin47e!'

    HOSTS = ['app1.example.com', 'app2.example.com']

    def copy_my_project(host):
        pass

    def install_my_project(host):
        pass

    def restart_my_application(host):
        pass

    def install():
        client = WarthogClient(MY_LB_HOST, MY_LB_USER, MY_LB_PASS)

        for host in HOSTS:
            with client.disabled_context(host):
                copy_my_project(host)
                install_my_project(host)
                restart_my_application(host)


        print('Installed project on all servers!')


Disable SSL Verification
------------------------

If you are interacting with the load balancer over HTTPS but using a self-signed certificate,
you'll have to disable certification verification (or get proper cert!). This example will use
the Warthog library client with certification verification disabled.

.. code-block:: python

    from __future__ import print_function

    import time
    from warthog.api import get_transport_factory, CommandFactory, WarthogClient

    MY_LB_HOST = 'https://lb.example.com'
    MY_LB_USER = 'deploy'
    MY_LB_PASS = 'Depl0yin47e!'

    HOSTS = ['app1.example.com', 'app2.example.com']

    def copy_my_project(host):
        pass

    def install_my_project(host):
        pass

    def restart_my_application(host):
        pass

    def install():
        transport = get_transport_factory(verify=False)
        factory = CommandFactory(transport)
        client = WarthogClient(MY_LB_HOST, MY_LB_USER, MY_LB_PASS, commands=factory)

        for host in HOSTS:
            with client.disabled_context(host):
                copy_my_project(host)
                install_my_project(host)
                restart_my_application(host)


        print('Installed project on all servers!')

Using an INI-style Configuration File
-------------------------------------

Since version :doc:`0.4.0 </changes>`, Warthog includes a module for parsing expected
configuration settings. Using an external configuration file via this module allows you
to keep credentials for your load balancer in a separate, centralized, config file instead
of embedded in each deploy script.

Use of a configuration file is not required if you are using the :class:`warthog.client.WarthogClient`
class directly. However, if you are using the :doc:`cli`, a configuration file is required.

Refer to the :doc:`cli` documentation for more information about the specific syntax
and expected locations of the configuration file.

Below is an example of loading configuration settings from one of the default locations
for the configuration file.

.. code-block:: python

    from warthog.api import WarthogConfigLoader, WarthogClient

    HOSTS = ['app1.example.com', 'app2.example.com']

    def copy_my_project(host):
        pass

    def install_my_project(host):
        pass

    def restart_my_application(host):
        pass

    def install():
        # We aren't specifying a custom path for a config file. This means
        # we're letting the WarthogConfigLoader check each of the default
        # locations for a config file.
        config_loader = WarthogConfigLoader()
        settings = config_loader.parse_configuration()

        # Create a new instance of the client with settings we parsed from
        # the configuration file. Hooray no hardcoded user and password!
        client = WarthogClient(settings.scheme_host, settings.username, settings.password)

        for host in HOSTS:
            client.disable_server(host)

            copy_my_project(host)
            install_my_project(host)
            restart_my_application(host)

            client.enable_server(host)

        print('Installed project on all servers!')
