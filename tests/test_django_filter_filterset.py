from unittest import SkipTest

from django.conf.urls import include, url
from django.test import TestCase
from django.test.utils import override_settings

from rest_framework import routers, viewsets
from rest_framework.test import APIClient

from albums.models import Album
from albums.serializers import AlbumSerializer

# Skip this module if django-filter is not available
try:
    from django_filters import rest_framework as filters
    from rest_framework_datatables.django_filters.backends import (
        DatatablesFilterBackend)
    from rest_framework_datatables.django_filters.filterset import (
        DatatablesFilterSet)
except ImportError:
    raise SkipTest('django-filter not available')


@override_settings(ROOT_URLCONF=__name__)
class TestWithViewSet(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.client = APIClient()


class AlbumRegexFilter(DatatablesFilterSet):
    """Filter name, artist and genre by name with icontains"""

    name = filters.CharFilter(lookup_expr='icontains')
    genres = filters.CharFilter(lookup_expr='name__icontains', distinct=True)
    artist = filters.CharFilter(lookup_expr='name__icontains')

    class Meta:
        model = Album
        fields = '__all__'


class AlbumRegexViewSet(viewsets.ModelViewSet):
    """ViewSet for the Album model under /api/albums with regex support

    Identical to the icontains test, we just change the lookup
    expression based on the regex field.

    """

    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [DatatablesFilterBackend]
    filterset_class = AlbumRegexFilter


router = routers.DefaultRouter()
router.register(r'albums', AlbumRegexViewSet)


urlpatterns = [
    url('^api/', include(router.urls)),
]


# repeat the tests for icontains, as the regex functionality is
# optional
class TestIcontainsOne(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=name'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=on')
        self.assertEqual(self.result.status_code, 200)

    def test(self):
        self.assertEqual(self.result.json()['recordsTotal'], 15)
        self.assertEqual(self.result.json()['recordsFiltered'], 6)


class TestIcontainsTwo(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=name'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=on'
            '&columns[1][data]=genres'
            '&columns[1][searchable]=true'
            '&columns[1][search][value]=blues')
        self.assertEqual(self.result.status_code, 200)

    def test(self):
        self.assertEqual(self.result.json()['recordsTotal'], 15)
        self.assertEqual(self.result.json()['recordsFiltered'], 2)


class TestFilterRegex(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=artist'
            '&columns[0][searchable]=true'
            '&columns[0][search][regex]=true'
            '&columns[0][search][value]=^bob')
        self.data = self.result.json()

    def test(self):
        self.assertEqual(self.result.status_code, 200)
        self.assertEqual(self.data['recordsFiltered'], 2)
        self.assertEqual(self.data['recordsTotal'], 15)
        self.assertEqual(self.data['data'][0]['artist']['name'],
                         'Bob Dylan')
        self.assertEqual(self.data['data'][1]['artist']['name'],
                         'Bob Dylan')


class TestFilterRegexTwo(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=artist'
            '&columns[0][searchable]=true'
            '&columns[0][search][regex]=true'
            '&columns[0][search][value]=^bob'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&columns[1][search][regex]=true'
            '&columns[1][search][value]=^b.*on.*e$')
        self.data = self.result.json()

    def test(self):
        self.assertEqual(self.result.status_code, 200)
        self.assertEqual(self.data['recordsFiltered'], 1)
        self.assertEqual(self.data['recordsTotal'], 15)
        self.assertEqual(self.data['data'][0]['artist']['name'],
                         'Bob Dylan')
        self.assertEqual(self.data['data'][0]['name'],
                         'Blonde on Blonde')


class TestFilterRegexIcontains(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=artist'
            '&columns[0][searchable]=true'
            '&columns[0][search][regex]=true'
            '&columns[0][search][value]=^bob'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&columns[1][search][regex]=False'
            '&columns[1][search][value]=way')
        self.data = self.result.json()

    def test(self):
        self.assertEqual(self.result.status_code, 200)
        self.assertEqual(self.data['recordsFiltered'], 1)
        self.assertEqual(self.data['recordsTotal'], 15)
        self.assertEqual(self.data['data'][0]['artist']['name'],
                         'Bob Dylan')
        self.assertEqual(self.data['data'][0]['name'],
                         'Highway 61 Revisited')


class TestFilterIcontainsRegex(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=artist'
            '&columns[0][searchable]=true'
            '&columns[0][search][regex]=false'
            '&columns[0][search][value]=ylan'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&columns[1][search][regex]=true'
            '&columns[1][search][value]=^Highway')
        self.data = self.result.json()

    def test(self):
        self.assertEqual(self.result.status_code, 200)
        self.assertEqual(self.data['recordsFiltered'], 1)
        self.assertEqual(self.data['recordsTotal'], 15)
        self.assertEqual(self.data['data'][0]['artist']['name'],
                         'Bob Dylan')
        self.assertEqual(self.data['data'][0]['name'],
                         'Highway 61 Revisited')
