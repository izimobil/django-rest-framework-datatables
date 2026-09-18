from albums.models import Album
from albums.serializers import AlbumSerializer

from django.db import connection
from django.urls import path
from django.test.utils import CaptureQueriesContext, override_settings
from django.test import TestCase

from rest_framework.generics import ListAPIView
from rest_framework.test import (
    APIClient,
)
from rest_framework.filters import BaseFilterBackend
from rest_framework_datatables.pagination import (
    DatatablesLimitOffsetPagination,
)
from rest_framework_datatables.filters import (
    DatatablesFilterBackend, count_rows)


class CustomFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(name__istartswith='a')


class CustomCountFilterBackend(DatatablesFilterBackend):
    """
    Override before and after counts to demonstrate performance fix.
    """

    def get_queryset_count_before(self, request, queryset, view):
        return 999

    def get_queryset_count_after(self, request, queryset, view):
        return 99


class TestFilterTestCase(TestCase):
    class TestAPIView(ListAPIView):
        serializer_class = AlbumSerializer
        pagination_class = DatatablesLimitOffsetPagination
        datatables_additional_order_by = 'year'

        def get_queryset(self):
            return Album.objects.all()


    class TestAPIView2(ListAPIView):
        serializer_class = AlbumSerializer
        filter_backends = [CustomFilterBackend, DatatablesFilterBackend]

        def get_queryset(self):
            return Album.objects.all()

    class TestAPIView3(ListAPIView):
        serializer_class = AlbumSerializer
        filter_backends = [DatatablesFilterBackend]

        def get_queryset(self):
            return Album.objects.all()

    class TestAPIView4(ListAPIView):
        serializer_class = AlbumSerializer
        filter_backends = [CustomCountFilterBackend]

        def get_queryset(self):
            return Album.objects.all()

    fixtures = ['test_data']

    def setUp(self):
        self.client = APIClient()

    @override_settings(ROOT_URLCONF=__name__)
    def test_additional_order_by(self):
        response = self.client.get('/api/additionalorderby/?format=datatables&draw=1&columns[0][data]=rank&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=artist_name&columns[1][name]=artist.name&columns[1][searchable]=true&columns[1][orderable]=true&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=name&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&order[0][column]=1&order[0][dir]=desc&start=4&length=1&search[value]=&search[regex]=false')
        # Would be "Sgt. Pepper's Lonely Hearts Club Band" without the additional order by
        expected = (15, 15, 'Rubber Soul')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    @override_settings(ROOT_URLCONF=__name__)
    def test_multiple_filters_backend1(self):
        response = self.client.get('/api/multiplefilterbackends/?format=datatables&columns[0][data]=name&columns[0][searchable]=true&columns[1][data]=artist__name&columns[1][searchable]=true&search[value]=are+you+exp')
        expected = (1, 15, 'Are You Experienced')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    @override_settings(ROOT_URLCONF=__name__)
    def test_multiple_filters_backend2(self):
        response = self.client.get('/api/multiplefilterbackends/?format=datatables&columns[0][data]=name&columns[0][searchable]=true&columns[1][data]=artist__name&columns[1][searchable]=true&search[value]=white')
        expected = (0, 15)
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal']), expected)

    @override_settings(ROOT_URLCONF=__name__)
    def test_search_over_filters_backend1(self):
        """Search over all columns

        Searches should be made over all columns data
        (It can be manual tested on 'Full example with foreign key and many to many relation' table)

        """
        response = self.client.get('/api/filter/albums/?format=datatables&length=10&columns[0][data]=rank&columns[0][searchable]=false&columns[1][data]=artist.name&columns[1][searchable]=true&columns[2][data]=name&columns[2][searchable]=true&columns[3][data]=year&columns[3][searchable]=true&columns[3][search][value]=1966&columns[4][data]=genres.name&columns[4][searchable]=true&search[value]=Blues')
        expected = (1, 15)

        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal']), expected)

    @override_settings(ROOT_URLCONF=__name__)
    def test_custom_count_before(self):
        response = self.client.get('/api/customcounts/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[value]=are+you+exp')
        result = response.json()
        self.assertEqual(result['recordsTotal'], 999)

    @override_settings(ROOT_URLCONF=__name__)
    def test_custom_count_after(self):
        response = self.client.get('/api/customcounts/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[value]=are+you+exp')
        result = response.json()
        self.assertEqual(result['recordsFiltered'], 99)

    @override_settings(ROOT_URLCONF=__name__)
    def test_distinct_count_dedupes_the_primary_key(self):
        """The filtered count should not dedupe every selected column

        A search that reaches a many to many relation makes the queryset
        distinct, and counting it used to make the database dedupe whole
        rows.

        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/filter/albums/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&columns[1][data]=genres.name&columns[1][searchable]=true&search[value]=blues')
        counts = [
            query['sql'] for query in queries.captured_queries
            if query['sql'].upper().startswith('SELECT COUNT')
        ]
        self.assertEqual(response.json()['recordsFiltered'], 4)
        self.assertIn('SELECT DISTINCT', counts[-1])
        self.assertNotIn('"albums_album"."year"', counts[-1])

    def test_count_rows_keeps_a_values_projection(self):
        """A distinct projection is counted by the columns it selects

        Counting by primary key would replace the projection, and count
        albums rather than distinct artists.

        """
        for queryset in (
            Album.objects.values('artist').distinct(),
            Album.objects.values_list('artist', flat=True).distinct(),
        ):
            self.assertLess(queryset.count(), Album.objects.count())
            self.assertEqual(count_rows(queryset), queryset.count())

    def test_count_rows_keeps_extra_select_columns(self):
        """A distinct queryset is counted by the extra() columns it selects

        A column from a to-many join makes rows distinct that share a
        primary key, so counting by primary key would count too few.

        """
        queryset = Album.objects.filter(
            genres__name__icontains='o'
        ).extra(select={'genre_name': '"albums_genre"."name"'}).distinct()
        self.assertGreater(
            queryset.count(), queryset.order_by().values('pk').distinct().count())
        self.assertEqual(count_rows(queryset), queryset.count())

    @override_settings(ROOT_URLCONF=__name__)
    def test_custom_count_unfiltered(self):
        """An overridden count after filtering is used on every draw"""
        response = self.client.get('/api/customcounts/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true')
        result = response.json()
        self.assertEqual(result['recordsFiltered'], 99)

    @override_settings(ROOT_URLCONF=__name__)
    def test_search_over_filters_backend2(self):
        response = self.client.get('/api/filter/albums/?format=datatables&length=10&columns[0][data]=rank&columns[0][searchable]=false&columns[1][data]=artist.name&columns[1][searchable]=true&columns[2][data]=name&columns[2][searchable]=true&columns[3][data]=year&columns[3][searchable]=true&columns[3][search][value]=1967&columns[4][data]=genres.name&columns[4][searchable]=true&search[value]=Velvet')
        expected = (1, 15)

        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal']), expected)

urlpatterns = [
    path('api/additionalorderby/', TestFilterTestCase.TestAPIView.as_view()),
    path('api/multiplefilterbackends/', TestFilterTestCase.TestAPIView2.as_view()),
    path('api/filter/albums/', TestFilterTestCase.TestAPIView3.as_view()),
    path('api/customcounts/', TestFilterTestCase.TestAPIView4.as_view()),
]
