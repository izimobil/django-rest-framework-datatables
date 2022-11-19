from albums.models import Album
from albums.serializers import AlbumSerializer

from django.urls import path
from django.test.utils import override_settings
from django.test import TestCase

from rest_framework.generics import ListAPIView
from rest_framework.test import (
    APIClient,
)
from rest_framework.filters import BaseFilterBackend
from rest_framework_datatables.pagination import (
    DatatablesLimitOffsetPagination,
)
from rest_framework_datatables.filters import DatatablesFilterBackend


class CustomFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(name__istartswith='a')


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
    def test_search_over_filters_backend2(self):
        response = self.client.get('/api/filter/albums/?format=datatables&length=10&columns[0][data]=rank&columns[0][searchable]=false&columns[1][data]=artist.name&columns[1][searchable]=true&columns[2][data]=name&columns[2][searchable]=true&columns[3][data]=year&columns[3][searchable]=true&columns[3][search][value]=1967&columns[4][data]=genres.name&columns[4][searchable]=true&search[value]=Velvet')
        expected = (1, 15)

        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal']), expected)

urlpatterns = [
    path('api/additionalorderby/', TestFilterTestCase.TestAPIView.as_view()),
    path('api/multiplefilterbackends/', TestFilterTestCase.TestAPIView2.as_view()),
    path('api/filter/albums/', TestFilterTestCase.TestAPIView3.as_view()),
]
