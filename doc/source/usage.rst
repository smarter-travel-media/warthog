Usage
=====

Descriptions and examples of how to make use of the Warthog library in common deploy-related
situations are outlined below.

Each of the examples will create a new instance of the Warthog client but, obviously, you do
not need to do this in your actual deploy process. In fact, you can even share the same client
instance between multiple threads (it's thread safe and immutable).

Create a Client
---------------

Let's start with the simplest possible thing you can do, just create a client instance.

.. code-block:: python

    from warthog.api import WarthogClient

    client = WarthogClient('https://lb.example.com', 'deploy', 'my password')

In the code above, we create a new client instance with the following properties:

* It will connect to the load balancer at ``lb.example.com``.
* It will connect over HTTPS and it will validate the certificate presented by the
  load balancer.
* It will use the user 'deploy' and the password 'my password' for authentication.

You'll notice that we didn't tell the client to validate the certificate presented by
the load balancer but it will attempt to do that anyway. That is because the client
attempts to be safe by default. We'll explain how to disable this later.

Create a Client Without SSL Verification
----------------------------------------

It might be the case that you use a self-signed certificate for HTTPS connections to
your load balancer. This isn't ideal, but hey, it happens. To this end, you can configure
the Warthog library to connect over HTTPS but *not* to verify the SSL certificate.

This can be easily accomplished by passing an extra argument to the client when
creating it.

.. code-block:: python

    from warthog.api import WarthogClient

    client = WarthogClient(
        'https://lb.example.com', 'deploy', 'my password', verify=False)


Create a Client With an Alternate SSL/TLS Version
-------------------------------------------------

If you need to use an alternate version of SSL or TLS to interact with your load balancer
over HTTPS, you can accomplish this by just passing an extra argument to the client when
creating it.

.. code-block:: python

    import ssl
    from warthog.api import WarthogClient

    client = WarthogClient(
        'https://lb.example.com', 'deploy', 'my password', ssl_version=ssl.PROTOCOL_TLSv1_2)



Create a Client From a Configuration File
-----------------------------------------

Hopefully, the thought of sprinkling your load balancer credentials throughout your deploy
scripts makes you nervous. Luckily, there's functionality in the Warthog library for reading
configuration information about the load balancer from an external file.

For more details about the format of this file and the default expected locations, see the
:doc:`cli` section.

Let's start by importing all the parts of the API that we'll need.

.. code-block:: python

    from warthog.api import WarthogClient, WarthogConfigLoader

The ``WarthogConfigLoader`` class can load configuration from an explicit path or it can check
several expected locations for the file. Let's start with loading an explicit path.

.. code-block:: python

    config_loader = WarthogConfigLoader(config_file='/etc/load-balancer.ini')

At this point, we haven't actually loaded anything. Let's do that next.

.. code-block:: python

     config_loader.initialize()
     config_settings = config_loader.get_settings()

Now we're talking! At this point, we have an immutable struct-like object (a named tuple in Python
parlance) with all the needed values for creating a new ``WarthogClient`` instance. Let's do that
now.

.. code-block:: python

    client = WarthogClient(
        config_settings.scheme_host, config_settings.username, config_settings.password,
        verify=config_settings.verify, ssl_version=config_settings.ssl_version)

Disable a Server
----------------

If you're using the Warthog library as part of your deploy process, one of the first things you'll
need to do is safely remove a server from receiving traffic in the load balancer. Let's explore that
below.

First, create the client instance that we'll be using.

.. code-block:: python

    from warthog.api import WarthogClient

    client = WarthogClient('https://lb.example.com', 'deploy', 'my password')

Next, we'll mark a server as disabled in the load balancer, letting the client use retry logic to
attempt to do this as safely as possible. Note that the server is specified by hostname alone.

.. code-block:: python

    client.disable_server('app1.example.com')

You might notice that this method doesn't return immediately, it takes a little bit. That's because
when we disable a server by default we:

* Mark the server as disabled, attempting this a few times if there are errors making
  the disable request.
* Check the number of active connections to the server every few seconds, waiting until
  this number reaches zero.
* After waiting up to a maximum amount of time for the number of connections on the server
  to reach zero, check if the server actually got disabled.

It might be the case that you don't really need to wait for the number of connections to
reach zero. If this is the case, you can tell the client not to use retry logic or wait
for the number of connections to drop to zero.

.. code-block:: python

    client.disable_server('app1.example.com', max_retries=0)

You can set ``max_retries`` to any number that makes sense for your deploy process. Each
retry will be attempted two seconds apart by default. See :class:`warthog.client.WarthogClient`
for more information about how to change the time between retries.

Enable a Server
---------------

After you've deployed a new version of your application to a server or restarted it, you'll need
to enable the server so that it starts receiving traffic from the load balancer. The method for
doing this is very similar to how disabling a server works. We'll go into it more below.

First, create the client instance that we'll be using.

.. code-block:: python

    from warthog.api import WarthogClient

    client = WarthogClient('https://lb.example.com', 'deploy', 'my password')

Next, we'll mark a server as enabled in the load balancer, letting the client use retry logic
to make sure that the server actually ends up enabled. Note that the server is specified by
hostname alone.

.. code-block:: python

    client.enable_server('app1.example.com')

Similar to disabling a server, this method won't return immediately. When we enable server by
default we:

* Mark the server as enabled, attempting this a few times if there are errors making
  the enable request.
* Check the status of the server, waiting until it becomes 'enabled'
* After waiting up to a maximum amount of time for the server to become enabled, check if the
  server actually got enabled.

Similar to disabling a server, it might be the case that you don't really need to wait for
a server to become enabled. If this is the case, you can tell the client not to use retry logic
or wait for the server to become enabled.

.. code-block:: python

    client.enable_server('app1.example.com', max_retries=0)

You can set ``max_retries`` to any number that makes sense for your deploy process. Each
retry will be attempted two seconds apart by default. See :class:`warthog.client.WarthogClient`
for more information about how to change the time between retries.

Non-Load Balanced Servers
-------------------------

If you use the same deployment process for servers that are in a load balancer and servers that
aren't in a load balancer, you'll have to deal with that when you use the Warthog library.

When you attempt to enable, disable, or otherwise interact with a non-load balanced host through
the load balancer you'll get an exception (:class:`warthog.exceptions.WarthogNoSuchNodeError`)
indicating that this is not a host that the load balancer knows about. Let's look at how to handle
this situation below.

First, create the client instance that we'll be using.

.. code-block:: python

    from warthog.api import WarthogClient, WarthogNoSuchNodeError

    client = WarthogClient('https://lb.example.com', 'deploy', 'my password')

Next we'll attempt to disable the server as part of our deploy process, but we'll catch the
exception raised when the server isn't recognized by the load balancer.

.. code-block:: python

    try:
        client.disable_server('app1.example.com')
    except WarthogNoSuchNodeError:
        use_lb = False
    else:
        use_lb = True

    # Your deploy process goes here...

    if use_lb:
        client.enable_server('app1.example.com')

You can see above that we catch the exception that indicates this is not a host that the load
balancer knows about. In this case, we make sure to not attempt to enable the server after completing
our deployment (or application restart, etc.).

Already Disabled Servers
------------------------

Sometimes a server gets marked as disabled in a load balancer outside of your deploy process. Maybe
the server is being used for load testing, maybe some maintenance is being performed. Whatever the
reason, it'd be nice if your deploy process recognized that this server is disabled and that it should
not be put back into active use in the load balancer. We'll go over how to do this using the Warthog
library below.

First, create the client instance that we'll be using.

.. code-block:: python

    from warthog.api import WarthogClient, STATUS_DISABLED

    client = WarthogClient('https://lb.example.com', 'deploy', 'my password')

Next, we'll check the current status of the node when deploying to it.

.. code-block:: python

    already_disabled = STATUS_DISABLED == client.get_status('app1.example.com')

If the server was already disabled when we found it, we don't need to disable it before
deploying to it.

.. code-block:: python

    if not already_disabled:
        client.disable_server('app1.example.com')

    # Your deploy process goes here...

    if not already_disabled:
        client.enable_server('app1.example.com')

You can see above that:

* If the server was *disabled* when we found it, we didn't disable it before deploying and we didn't
  enable it after deploying.
* If the server was *enabled* when we found it, we disabled it before deploying and enabled it afterwards.

Summary
-------

Hopefully, these use cases and examples will give you a good idea of how to incorporate the Warthog
library into your deploy process.
