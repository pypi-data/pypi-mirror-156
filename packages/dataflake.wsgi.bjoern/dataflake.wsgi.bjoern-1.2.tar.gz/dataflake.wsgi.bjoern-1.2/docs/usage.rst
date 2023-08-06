Using this package
==================

.. warning::

   Bjoern does not use Python logging facilities when encountering errors. It
   just writes to ``STDERR``. That means you will see exception output on the
   console if you run the application in the foreground, but not in the
   configured event log.


Using the PasteDeploy entry point
---------------------------------
You can use the PasteDeploy entry point in your WSGI configuration file to
define a ``bjoern`` server:

.. code-block:: ini

   [server:main]
   use = egg:dataflake.wsgi.bjoern#main
   host = 127.0.0.1
   port = 8080
   reuse_port = True

If you leave out the ``host`` specification, ``bjoern``  will listen on all
IPv4 interfaces (`0.0.0.0`). If no port is specified ``bjoern`` will choose a
random port (probably not what you want). ``reuse_port`` sets ``SO_REUSEPORT``
if it is available on your platform.

Alternatively you could use ``listen`` directive instead of ``host`` and ``port``:

.. code-block:: ini

   [server:main]
   use = egg:dataflake.wsgi.bjoern#main
   listen = 127.0.0.1:8080
   reuse_port = True

.. code-block:: ini

   [server:main]
   use = egg:dataflake.wsgi.bjoern#main
   listen = 8080
   reuse_port = True


Creating a basic WSGI configuration for Zope
--------------------------------------------
This package defines a console script named ``mkbjoerninstance`` that works
just like Zope's own ``mkwsgiinstance``. It will ask you for a location, a
username and a password to create a basic Zope instance home with a WSGI
configuration, in this case it will be ``bjoern``-based as opposed to Zope's
default, ``waitress``.

.. note::

   Just like ``mkwsgiinstance``, the script will not overwrite an existing WSGI
   configuration file at ``etc/zope.ini``. You need to move the existing file
   to the side to get a fresh configuration.

.. code-block:: console

   $ bin/mkbjoerninstance
   Please choose a directory in which you'd like to install
   Zope "instance home" files such as database files, configuration
   files, etc.
   
   Directory: .
   Please choose a username and password for the initial user.
   These will be the credentials you use to initially manage
   your new Zope instance.
   
   Username: admin
   Password: (enter password)
   Verify password: (re-enter password)
