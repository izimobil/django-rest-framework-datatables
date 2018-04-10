djangorestframework-datatables
======================================

|build-status-image| |coveralls-image| |pypi-version|

Overview
--------

Seamless integration between Django REST framework and Datatables (https://datatables.net).

When you call your API with ``?format=datatables`` it will return a JSON structure that is fully compatible with what Datatables expects.
It handles searching, filtering, ordering and most usecases you can imagine with Datatables.

The great benefit of django-rest-framework-datatables is that you don't have to create a different API, your API will be untouched unless you specify the datatables format on your request.

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

Quickstart
----------

Add ``rest_framework_datatables`` to INSTALLED_APPS.

Edit your REST_FRAMEWORK settings to match the following:

.. code:: python

    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
            'rest_framework_datatables.renderers.DatatablesRenderer',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'rest_framework_datatables.filters.DatatablesFilterBackend',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
        'PAGE_SIZE': 50,
    }

In your serializers you must inherit from ``rest_framework_datatables.DatatablesModelSerializer`` or ``rest_framework_datatables.DatatablesHyperlinkedModelSerializer``.

An example of Datatables (HTML/JS):

.. code:: html

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Rolling Stone Top 500 albums of all time</title>
      <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0/css/bootstrap.css">
      <link rel="stylesheet" href="//cdn.datatables.net/1.10.16/css/dataTables.bootstrap4.min.css">
    </head>
    
    <body>
      <div class="container">
        <div class="row">
          <div class="col-sm-12">
            <table id="albums" class="table table-striped table-bordered" style="width:100%">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Artist</th>
                  <th>Album name</th>
                  <th>Year</th>
                  <th>Genres</th>
                </tr>
              </thead>
            </table>
          </div>
        </div>
      </div>
      <script src="//code.jquery.com/jquery-1.12.4.js"></script>
      <script src="//cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js"></script>
      <script src="//cdn.datatables.net/1.10.16/js/dataTables.bootstrap4.min.js"></script>
      <script>
          $(document).ready(function() {
              var table = $('#albums').DataTable({
                  "serverSide": true,
                  "ajax": "/api/albums/?format=datatables",
                  "columns": [
                      {"data": "rank", "searchable": false},
                      {"data": "artist_name", "name": "artist.name"},
                      {"data": "name"},
                      {"data": "year"},
                      {"data": "genres", "name": "genres.name", "sortable": false},
                  ]
              });
          });
      </script>
    </body>
    </html>

Example project
---------------

To play with the example project, just clone the repository and run the dev server.

.. code:: bash

    $ git clone https://github.com/izimobil/django-rest-framework-datatables.git
    $ cd django-rest-framework-datatables
    $ python example/manage.py runserver
    $ firefox http://127.0.0.1:8000

Testing
-------

Install development requirements.

.. code:: bash

    $ pip install -r requirements-dev.txt

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
.. |coveralls-image| image:: https://coveralls.io/repos/izimobil/django-rest-framework-datatables/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/izimobil/django-rest-framework-datatables?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-datatables.svg
   :target: https://pypi.python.org/pypi/djangorestframework-datatables
