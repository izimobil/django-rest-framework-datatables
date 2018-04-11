Quickstart
==========

Installation
------------

Just use ``pip``:

.. code:: bash

    $ pip install djangorestframework-datatables

Configuration
-------------

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

What have we done so far ?

- we added the ``rest_framework_datatables.renderers.DatatablesRenderer`` to existings renderers
- we added the ``rest_framework_datatables.filters.DatatablesFilterBackend`` to the filter backends
- we replaced the pagination class by ``rest_framework_datatables.pagination.DatatablesPageNumberPagination``

.. note::

    If you are using ``rest_framework.pagination.LimitOffsetPagination`` as pagination class, relax and don't panic !
    django-rest-framework-datatables can handle that, just replace it with ``rest_framework_datatables.pagination.DatatablesLimitOffsetPagination``.

And that's it !
---------------

Your API is now fully compatible with Datatables and will provide searching, filtering, ordering and pagination without any modification of your API code, to continue, follow the :doc:`tutorial<tutorial>`.
