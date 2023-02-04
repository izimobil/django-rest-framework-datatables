django-rest-framework-datatables
================================

|build-status-image| |codecov-image| |documentation-status-image| |pypi-version| |py-versions|

Overview
--------

This package provides seamless integration between `Django REST framework <https://www.django-rest-framework.org>`_ and `Datatables <https://datatables.net>`_.

Install django-rest-framework-datatables, call your API with ``?format=datatables`` and it will return a JSON structure that is fully compatible with what Datatables expects.
It handles searching, filtering, ordering and most usecases you can imagine with Datatables.

The great benefit of django-rest-framework-datatables is that you don't have to create a different API, your API still work exactly the same unless you specify the ``datatables`` format on your request.

Full documentation is available on `Read the Docs <http://django-rest-framework-datatables.readthedocs.io/en/latest/>`_ !

You can play with a demo of the example app on `Python Anywhere <https://izimobil.pythonanywhere.com>`_.

Requirements
------------

- Python (3.7, 3.8, 3.9, 3.10)
- Django (3.2, 4.0, 4.1)
- Django REST Framework (3.14)

We highly recommend and only officially support the latest patch release of each Python, Django and Django Rest Framework series.

Quickstart
----------

Installation
~~~~~~~~~~~~

Just use ``pip``:

.. code:: bash

    $ pip install djangorestframework-datatables

Configuration
~~~~~~~~~~~~~

To enable Datatables support in your project, add ``'rest_framework_datatables'`` to your ``INSTALLED_APPS``, and modify your ``REST_FRAMEWORK`` settings like this:

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

And that's it !
~~~~~~~~~~~~~~~

Your API is now fully compatible with Datatables and will provide searching, filtering, ordering and pagination without any modification of your API code !

Always Serialize Specific Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sometimes you may want to expose fields regardless of datatable's url parameters. You can do so by setting the ``datatables_always_serialize`` tuple like so:

.. code:: python

    class ArtistSerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(read_only=True)
    
        class Meta:
            model = Artist
            fields = (
                'id', 'name',
            )
            datatables_always_serialize = ('id',)

An example of Datatable
~~~~~~~~~~~~~~~~~~~~~~~

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

`Install poetry <https://python-poetry.org/docs/#installation>`_ if not already installed.

.. code:: bash

    $ git clone https://github.com/izimobil/django-rest-framework-datatables.git
    $ cd django-rest-framework-datatables
    $ poetry install --with dev
    $ python example/manage.py runserver
    $ firefox http://127.0.0.1:8000

Testing
-------

`Install poetry <https://python-poetry.org/docs/#installation>`_ if not already installed.

Install development requirements.

.. code:: bash

    $ poetry install --with dev

Run the tests.

.. code:: bash

    $ python example/manage.py test

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

If you want to check the coverage, use:

.. code:: bash

    $ coverage run ./example/manage.py test
    $ coverage report -m

Documentation
-------------

The documentation is available online on `Read the Docs <http://django-rest-framework-datatables.readthedocs.io/en/latest/>`_.

To build the documentation, you’ll need to install ``sphinx``.

.. code:: bash

    $ poetry install --with docs

To build the documentation:

.. code:: bash

    $ cd docs
    $ make clean && make html

Publish to PyPI
---------------

`Build <https://python-poetry.org/docs/cli/#build>`_ package and `Publish <https://python-poetry.org/docs/cli/#publish>`_ to PyPI with two commands.

.. code:: bash

    $ poetry build
    $ poetry publish

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://api.travis-ci.com/izimobil/django-rest-framework-datatables.svg?branch=master
   :target: http://travis-ci.com/izimobil/django-rest-framework-datatables?branch=master
   :alt: Travis build

.. |codecov-image| image:: https://codecov.io/gh/izimobil/django-rest-framework-datatables/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/izimobil/django-rest-framework-datatables

.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-datatables.svg
   :target: https://pypi.python.org/pypi/djangorestframework-datatables
   :alt: Pypi version

.. |documentation-status-image| image:: https://readthedocs.org/projects/django-rest-framework-datatables/badge/?version=latest
   :target: http://django-rest-framework-datatables.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |py-versions| image:: https://img.shields.io/pypi/pyversions/djangorestframework-datatables.svg
   :target: https://img.shields.io/pypi/pyversions/djangorestframework-datatables.svg
   :alt: Python versions

.. |dj-versions| image:: https://img.shields.io/pypi/djversions/djangorestframework-datatables.svg
   :target: https://img.shields.io/pypi/djversions/djangorestframework-datatables.svg
   :alt: Django versions
