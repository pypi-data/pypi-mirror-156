Installation
============
You will need `Python <http://python.org>`_ 2.7 or 3.5 and higher to install
and use :mod:`dataflake.wsgi.bjoern`.

Bjoern itself requires the ``libev`` developer packages. Install them before
you install this package:

.. code-block:: console

   $ sudo apt-get install -y libev-dev  # <- Ubuntu
   $ sudo yum -y install libev-devel    # <- RHEL/CentOS

It is advisable to install :mod:`dataflake.wsgi.bjoern` into a
:term:`virtualenv` or similar environment like a buildout from
:mod:`zc.buildout` to obtain isolation from any "system" packages you've got
installed in your Python version (and likewise, to prevent
:mod:`dataflake.wsgi.bjoern` from globally installing versions of packages
that are not compatible with your system Python).

Setuptools/Distutils::

  $ easy_install dataflake.wsgi.bjoern

Pip::

  $ pip install dataflake.wsgi.bjoern

If you use :mod:`zc.buildout` you can add :mod:`dataflake.wsgi.bjoern`
to the necessary ``eggs`` section to have it pulled in automatically::

    ...
    eggs =
        dataflake.wsgi.bjoern
    ...

