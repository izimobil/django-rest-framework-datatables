djangorestframework-datatables
======================================

|build-status-image| |pypi-version|

Overview
--------

Seamless integration between Django REST framework and Datatables (https://datatables.net)

Requirements
------------

-  Python (2.7, 3.4, 3.5, 3.6)
-  Django (1.9, 1.10, 1.11, 2.0)
-  Django REST Framework (3.5, 3.6, 3.7, 3.8)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install djangorestframework-datatables

Example
-------

TODO

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ python example/manage.py test

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

To build the documentation, you’ll need to install ``sphinx``.

.. code:: bash

    $ pip install sphinx

To build the documentation:

.. code:: bash

    $ cd docs
    $ make

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/izimobil/django-rest-framework-datatables.svg?branch=master
   :target: http://travis-ci.org/izimobil/django-rest-framework-datatables?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-datatables.svg
   :target: https://pypi.python.org/pypi/djangorestframework-datatables
