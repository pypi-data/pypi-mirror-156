Development
===========

.. highlight:: console

Getting the source code
-----------------------
The source code is maintained on GitHub::

  $ git clone https://github.com/dataflake/dataflake.wsgi.werkzeug.git


Setting up a development sandbox and testing
--------------------------------------------
Once you've obtained a source checkout, you can follow these instructions to
perform various development tasks.  All development requires that you run the
buildout from the package root directory::

  $ python2.7 bootstrap.py
  $ bin/buildout

Once you have a buildout, the tests can be run as follows::

  $ bin/test


Building the documentation
--------------------------
The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ cd docs
  $ make html

The finished HTML files are under `docs/_build/html`.


Making a release
----------------
These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout::

  $ bin/buildout -N
  $ bin/buildout setup setup.py sdist bdist_wheel
  $ bin/twine upload -s dist/*

The ``bin/buildout`` step will make sure the correct package information 
is generated.
