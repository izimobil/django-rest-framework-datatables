django-rest-framework-datatables
=======================================

|build-status-image| |codecov-image| |documentation-status-image| |pypi-version| |py-versions|

Overview
--------

This package provides seamless integration between `Django REST framework <https://www.django-rest-framework.org>`_ and `Datatables <https://datatables.net>`_ with supporting `Datatables editor <https://editor.datatables.net>`_.

- It handles searching, filtering, ordering and most usecases you can imagine with Datatables.

Full documentation is available on `Read the Docs <http://django-rest-framework-datatables.readthedocs.io/en/latest/>`_ !

How to use
----------

Install
~~~~~~~

.. code:: bash

    $ pip install djangorestframework-datatables

If you need the functionality of the editor, you also need to download the data editor from  `here <https://editor.datatables.net/download/>`_, the JS+CSS version, and put the downloaded files in ``static`` folder.

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

For using Datatables editor you should use DatatablesEditorModelViewSet instead ModelViewSet or add EditorModelMixin to your views.

And that's it !
~~~~~~~~~~~~~~~

Your API is now fully compatible with Datatables and will provide searching, filtering, ordering and pagination without any modification of your API code ! For using Datatables editor you should use DatatablesEditorModelViewSet instead ModelViewSet or add EditorModelMixin to your views.

Configuring Datatables and Datatables editor
--------------------------------------------

- The URL for connecting datatables is the URL of your view with ``?format=datatables``
- The URL connecting datatables editor is the URL of your view with ``editor/``
- Full documentation is available on `Read the Docs <https://drf-datatables-editor.readthedocs.io/en/latest/>`_ !
- Also you'll need download `Datatables editor <https://editor.datatables.net>`_.

Example of HTML code:

.. code:: html



    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Rolling Stone Top 500 albums of all time</title>
        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.19/css/dataTables.bootstrap4.min.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/buttons/1.5.6/css/buttons.bootstrap4.min.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/select/1.3.0/css/select.bootstrap4.min.css">
        <link rel="stylesheet" href="/static/css/editor.bootstrap4.min.css">
    </head>
    <body>
        <div class="container" style="font-size: .9em;">
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
        <script src="//code.jquery.com/jquery-3.3.1.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/js/bootstrap.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap4.min.js"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.6/js/dataTables.buttons.min.js"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.6/js/buttons.bootstrap4.min.js"></script>
        <script src="https://cdn.datatables.net/select/1.3.0/js/dataTables.select.min.js"></script>
        <script src="/static/js/dataTables.editor.js"></script>
        <script src="/static/js/editor.bootstrap4.min.js"></script>
        <script>
            $(document).ready(function () {
                editor = new $.fn.dataTable.Editor({
                    ajax: "/api/albums/editor/?format=datatables",
                    table: "#albums",
                    fields: [{
                        label: "rank",
                        name: "rank",
                    }, {
                        label: "artist:",
                        name: "artist.id",
                        type: "select"
                    }, {
                        label: "name:",
                        name: "name",
                    }, {
                        label: "year:",
                        name: "year",
                    }]
                });
                var table = $('#albums').DataTable({
                    "serverSide": true,
                    dom: "Bfrtip",
                    "ajax": "/api/albums/?format=datatables",
                    "columns": [
                        {"data": "rank", "searchable": false},
                        {"data": "artist.name", "name": "artist.name"},
                        {"data": "name"},
                        {"data": "year"},
                        {"data": "genres", "name": "genres.name", "sortable": false},
                    ],
                    select: true,
                    buttons: [
                        {extend: "create", editor: editor},
                        {extend: "edit", editor: editor},
                        {extend: "remove", editor: editor}
                    ]
                });
                table.buttons().container()
                    .appendTo($('.col-md-6:eq(0)', table.table().container()));
            });
        </script>
    </body>
    </html>


Requirements
------------

-  Python (2.7, 3.4, 3.5, 3.6)
-  Django (1.11, 2.0, 2.1)
-  Django REST Framework (3.9)

Example project
---------------

To play with the example project, just clone the repository and run the dev server.

.. code:: bash

    $ git clone https://github.com/izimobil/django-rest-framework-datatables.git
    $ cd django-rest-framework-datatables
    Activate virtualenv.
    $ pip install -r requirements-dev.txt
    $ python example/manage.py runserver
    $ firefox http://127.0.0.1:8000

Testing
-------

Install development requirements.

.. code:: bash

    $ pip install -r requirements-dev.txt

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

    $ pip install -r requirements-docs.txt

To build the documentation:

.. code:: bash

    $ cd docs
    $ make clean && make build


.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/izimobil/django-rest-framework-datatables.svg?branch=master
   :target: http://travis-ci.org/izimobil/django-rest-framework-datatables?branch=master
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
