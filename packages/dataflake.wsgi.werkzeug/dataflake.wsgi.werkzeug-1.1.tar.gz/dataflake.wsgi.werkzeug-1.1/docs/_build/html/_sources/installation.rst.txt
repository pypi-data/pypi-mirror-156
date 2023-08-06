Installation
============
You will need `Python <http://python.org>`_ 2.7 or 3.5 and higher to install
and use :mod:`dataflake.wsgi.werkzeug`.

It is advisable to install :mod:`dataflake.wsgi.werkzeug` into a
:term:`virtualenv` or similar environment like a buildout from
:mod:`zc.buildout` to obtain isolation from any "system" packages you've got
installed in your Python version (and likewise, to prevent
:mod:`dataflake.wsgi.werkzeug` from globally installing versions of packages
that are not compatible with your system Python).

Setuptools/Distutils::

  $ easy_install dataflake.wsgi.werkzeug

Pip::

  $ pip install dataflake.wsgi.werkzeug

If you use :mod:`zc.buildout` you can add :mod:`dataflake.wsgi.werkzeug`
to the necessary ``eggs`` section to have it pulled in automatically::

    ...
    eggs =
        dataflake.wsgi.werkzeug
    ...

