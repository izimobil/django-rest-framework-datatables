Introduction
============

View tables
~~~~~~~~~~~

django-rest-framework-datatables provides seamless integration between `Django REST framework <https://www.django-rest-framework.org>`_ and `Datatables <https://datatables.net>`_.

Just call your API with ``?format=datatables``, and you will get a JSON structure that is fully compatible with what Datatables expects.

A "normal" call to your existing API will look like this:

.. code:: bash

    $ curl http://127.0.0.1:8000/api/albums/ | python -m "json.tool"

.. code:: json

    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "rank": 1,
                "name": "Sgt. Pepper's Lonely Hearts Club Band",
                "year": 1967,
                "artist_name": "The Beatles",
                "genres": "Psychedelic Rock, Rock & Roll"
            },
            {
                "rank": 2,
                "name": "Pet Sounds",
                "year": 1966,
                "artist_name": "The Beach Boys",
                "genres": "Pop Rock, Psychedelic Rock"
            }
        ]
    }

The same call with ``datatables`` format will look a bit different:

.. code:: bash

    $ curl http://127.0.0.1:8000/api/albums/?format=datatables | python -m "json.tool"

.. code:: json

    {
        "recordsFiltered": 2,
        "recordsTotal": 2,
        "draw": 1,
        "data": [
            {
                "rank": 1,
                "name": "Sgt. Pepper's Lonely Hearts Club Band",
                "year": 1967,
                "artist_name": "The Beatles",
                "genres": "Psychedelic Rock, Rock & Roll"
            },
            {
                "rank": 2,
                "name": "Pet Sounds",
                "year": 1966,
                "artist_name": "The Beach Boys",
                "genres": "Pop Rock, Psychedelic Rock"
            }
        ]
    }

As you can see, django-rest-framework-datatables automatically adapt the JSON structure to what Datatables expects. And you don't have to create a different API, your API will still work as usual unless you specify the ``datatables`` format on your request.

But django-rest-framework-datatables can do much more ! As you will learn in the tutorial, it speaks the Datatables language and can handle searching, filtering, ordering, pagination, etc.
Read the :doc:`quickstart guide<quickstart>` for instructions on how to install and configure django-rest-framework-datatables.


Editing tables
~~~~~~~~~~~~~~

The URL for interaction with the Datatables Editor: http://127.0.0.1:8000/api/albums/editor for this view.

You must set the parameter ``ajax: "/api/albums/editor/`` and that's it!
