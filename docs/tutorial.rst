Tutorial
========

.. note::

    The purpose of this section is not to replace the excellent `Django REST Framework documentation <https://www.django-rest-framework.org>`_ nor the `Datatables manual <https://datatables.net/manual/>`_, it is just to give you hints and gotchas for using your datatables compatible API.


Backend code
------------

So we have the following backend code, nothing very complicated if you are familiar with Django and Django REST Framework:

albums/models.py:

.. code:: python

    from django.db import models


    class Genre(models.Model):
        name = models.CharField('Name', max_length=80)

        class Meta:
            ordering = ['name']

        def __str__(self):
            return self.name


    class Artist(models.Model):
        name = models.CharField('Name', max_length=80)

        class Meta:
            ordering = ['name']

        def __str__(self):
            return self.name


    class Album(models.Model):
        name = models.CharField('Name', max_length=80)
        rank = models.PositiveIntegerField('Rank')
        year = models.PositiveIntegerField('Year')
        artist = models.ForeignKey(
            Artist,
            models.CASCADE,
            verbose_name='Artist',
            related_name='albums'
        )
        genres = models.ManyToManyField(
            Genre,
            verbose_name='Genres',
            related_name='albums'
        )

        class Meta:
            ordering = ['name']

        def __str__(self):
            return self.name

albums/serializers.py:

.. code:: python

    from rest_framework import serializers
    from .models import Album

    class ArtistSerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(read_only=True)

        # if we need to edit a field that is a nested serializer,
        # we must override to_internal_value method
        def to_internal_value(self, data):
            return get_object_or_404(Artist, pk=data['id'])

        class Meta:
            model = Artist
            fields = (
                'id', 'name',
            )


    class AlbumSerializer(serializers.ModelSerializer):
        artist = ArtistSerializer()
        genres = serializers.SerializerMethodField()

        def get_genres(self, album):
            return ', '.join([str(genre) for genre in album.genres.all()])

        class Meta:
            model = Album
            fields = (
                'rank', 'name', 'year', 'artist_name', 'genres',
            )

albums/views.py:

.. code:: python

    from django.shortcuts import render
    from rest_framework import viewsets
    from .models import Album
    from .serializers import AlbumSerializer


    def index(request):
        return render(request, 'albums/albums.html')


    class AlbumViewSet(EditorModelMixin, viewsets.ModelViewSet):
        queryset = Album.objects.all().order_by('rank')
        serializer_class = AlbumSerializer

urls.py:

.. code:: python

    from django.conf.urls import url, include
    from rest_framework import routers
    from albums import views


    router = routers.DefaultRouter()
    router.register(r'albums', views.AlbumViewSet)


    urlpatterns = [
        url('^api/', include(router.urls)),
        url('', views.index, name='albums')
    ]

A minimal datatable
-------------------

In this example, we will build a simple table that will list music albums, we will display 3 columns, the album rank, name and release year.
For the sake of simplicity we will also use HTML5 data attributes (which are supported by Datatables).

.. code:: html

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Rolling Stone Top 500 albums of all time</title>
      <meta name="description" content="Rolling Stone magazine's 2012 list of 500 greatest albums of all time with genres.">
      <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0/css/bootstrap.css">
      <link rel="stylesheet" href="//cdn.datatables.net/1.10.16/css/dataTables.bootstrap4.min.css">
    </head>

    <body>
      <div class="container">
        <div class="row">
          <div class="col-sm-12">
            <table id="albums" class="table table-striped table-bordered" style="width:100%" data-server-side="true" data-ajax="/api/albums/?format=datatables">
              <thead>
                <tr>
                  <th data-data="rank">Rank</th>
                  <th data-data="name">Album name</th>
                  <th data-data="year">Year</th>
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
              $('#albums').DataTable();
          });
      </script>
    </body>
    </html>

And that's it ! At this point, you should have a fully functional Datatable with search, ordering and pagination !

What we just did:

- included all the necessary CSS and JS files
- set the table ``data-server-side`` attribute to ``true``, to tell Datatables to use the server-side processing mode
- set the table ``data-ajax`` to our API URL with ``?format=datatables`` as query parameter
- set a ``data-data`` attribute for the two columns to tell Datatables what properties must be extracted from the response
- and finally initialized the Datatable via a javascript one-liner.


Perhaps you noticed that we didn't use all fields from our serializer in the above example, that's not a problem, django-rest-framework-datatables will automatically filter the fields that are not necessary when processing the request from Datatables.

If you want to force serialization of fields that are not requested by Datatables you can use the ``datatables_always_serialize`` Meta option in your serializer, here's an example:

.. code:: python

    class AlbumSerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(read_only=True)
        class Meta:
            model = Album
            fields = (
                'id', 'rank', 'name', 'year',
            )
            datatables_always_serialize = ('id', 'rank',)

In the above example, the fields 'id' and 'rank' will always be serialized in the response regardless of fields requested in the Datatables request.

.. hint::

    Alternatively, if you wish to choose which fields to preserve at runtime rather than hardcoding them into your serializer models, use the ``?keep=`` param along with the fields you wish to maintain (comma separated). For example, if you wished to preserve ``id`` and ``rank`` as before, you would simply use the following API call:

    .. code:: html

        data-ajax="/api/albums/?format=datatables&keep=id,rank"

In order to provide additional context of the data from the view, you can use the ``datatables_extra_json`` Meta option.

.. code:: python

    class AlbumViewSet(viewsets.ModelViewSet):
        queryset = Album.objects.all().order_by('rank')
        serializer_class = AlbumSerializer

        def get_options(self):
            return "options", {
                "artist": [{'label': obj.name, 'value': obj.pk} for obj in Artist.objects.all()],
                "genre": [{'label': obj.name, 'value': obj.pk} for obj in Genre.objects.all()]
            }

        class Meta:
            datatables_extra_json = ('get_options', )

In the above example, the 'get_options' method will be called to populate the rendered JSON with the key and value from the method's return tuple.

.. important::

    To sum up, **the most important things** to remember here are:
    
    - don't forget to add ``?format=datatables`` to your API URL
    - you must add a **data-data attribute** or specify the column data property via JS for each columns, the name must **match one of the fields of your DRF serializers**.


A more complex and detailed example with the ability to edit data
-----------------------------------------------------------------

In this example we want to display more informations about the album:

- the album artist name (``Album.artist`` is a foreignkey to ``Artist`` model)
- the genres (``Album.genres`` is a many to many relation with ``Genre`` model)

The HTML/JS code will look like this:

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

Notice that artist and genres columns have an extra data attribute: ``data-name``, this attribute is necessary to tell to the django-rest-framework-datatables builtin filter backend what field part to use to filter and reorder the queryset. The builtin filter will add ``__icontains`` to the string to perform the filtering/ordering.


.. hint::

    Datatables uses the dot notation in the ``data`` field to populate columns with nested data. In this example, ``artist.name`` refers to the field ``name`` within the nested serializer ``artist``.


Authorization
-------------

If you use user authorization you must sent a CSRF token with each POST request. To do this, you can use the following script:

.. code:: html

    <script>

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        var csrftoken = getCookie('csrftoken');

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

    </script>


Filtering
---------

Filtering is based off of the either the ``data`` or ``name`` fields. If you need to filter on multiple fields, you can always pass through multiple variables like so

.. code:: html

    <script>
        'columns': [
            {'data': 'artist.name', 'name': 'artist.name, artist__year'}
    </script>

This would allow you to filter the ``artist.name`` column based upon ``name`` or ``year``.

Because the ``name`` field is used to filter on Django queries, you can use either dot or double-underscore notation as shown in the example above.

The values within a single ``name`` field are tied together using a logical ``OR`` operator for filtering, while those between ``name`` fields are strung together with an ``AND`` operator. This means that Datatables' multicolumn search functionality is preserved.

If you need more complex filtering and ordering, you can always implement your own filter backend by inheriting from ``rest_framework_datatables.DatatablesFilterBackend``.

.. important::

    To sum up, for **foreign keys and relations** you need to specify a **name for the column** otherwise filtering and ordering will not work.


You can see this code live by running the :doc:`example app <example-app>`.


Handling Duplicates in Sorting
------------------------------
If sorting is done on a single column with more duplicates than the page size it's possible than some rows are never retrieved as we traverse through our datatable. This is because of how order by together with limit and offset works in the database.

As a workaround for this problem we add a second column to sort by in the case of ties.

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all().order_by('year')
    serializer_class = AlbumSerializer
    datatables_additional_order_by = 'rank'

    def get_options(self):
        return "options", {
            "artist": [{'label': obj.name, 'value': obj.pk} for obj in Artist.objects.all()],
            "genre": [{'label': obj.name, 'value': obj.pk} for obj in Genre.objects.all()]
        }

    class Meta:
        datatables_extra_json = ('get_options', )
