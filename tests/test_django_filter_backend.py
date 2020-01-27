from unittest import mock, SkipTest

from django.conf.urls import include, url
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework import routers, viewsets
from rest_framework.test import APIClient, APIRequestFactory

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


factory = APIRequestFactory()


class TestDFBackendTestCase(TestCase):

    fixtures = ['test_data']
    backend = DatatablesFilterBackend()


class TestNotDataTablesFormat(TestDFBackendTestCase):

    def test_format(self):
        qs = Album.objects.all()
        req = factory.get('ignored')
        req.accepted_renderer = mock.Mock()
        req.accepted_renderer.format = 'json'
        res = self.backend.filter_queryset(req, qs, None)
        self.assertEqual(res, qs)


# Most things are much easier to test with client and viewset, even
# though we're testing the backend here
class AlbumFilterViewSet(viewsets.ModelViewSet):
    """ViewSet for the Album model under /api/albums

    Simply not declaring any explicit fields and just giving '__all__'
    for filterset_fields will cause filtering for all model fields to
    "just work"[TM], with the following fields:

    artist: ModelChoiceField
    genres: ModelMultipleChoiceField
    name: CharField
    rank: DecimalField
    year: DecimalField

    See
    https://django-filter.readthedocs.io/en/master/ref/filterset.html#automatic-filter-generation-with-model
    and
    https://django-filter.readthedocs.io/en/master/guide/rest_framework.html#using-the-filterset-fields-shortcut
    for details.

    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [DatatablesFilterBackend]
    filterset_fields = '__all__'


@override_settings(ROOT_URLCONF=__name__)
class TestWithViewSet(TestDFBackendTestCase):

    def setUp(self):
        self.client = APIClient()


class TestUnfiltered(TestWithViewSet):

    def setUp(self):
        self.response = self.client.get('/api/albums/?format=datatables')
        self.view = self.response.renderer_context.get('view')


class TestNoFilterSet(TestUnfiltered):

    def setUp(self):
        with mock.patch.object(AlbumFilterViewSet, 'filterset_fields', None):
            super().setUp()

    def test_count_before(self):
        self.assertEqual(self.view._datatables_total_count, 15)

    def test_count_after(self):
        self.assertEqual(self.view._datatables_filtered_count, 15)


class TestCount(TestUnfiltered):

    def test_count_before(self):
        self.assertEqual(self.view._datatables_total_count, 15)

    def test_count_after(self):
        self.assertEqual(self.view._datatables_filtered_count, 15)


class TestFiltered(TestWithViewSet):

    def setUp(self):
        self.response = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=1971')
        self.json = self.response.json()

    def test_count_before(self):
        self.assertEqual(self.json['recordsTotal'], 15)

    def test_count_after(self):
        self.assertEqual(self.json['recordsFiltered'], 1)


class TestInvalid(TestWithViewSet):
    """Test handling invalid data

    Our artist (and genre) fields will automatically be multiple
    choice fields (assigned by django-filter), so we can test what
    happens if we pass an invalid (missing) choice

    """

    def setUp(self):
        self.response = self.client.get(
            '/api/albums/?format=datatables&length=10'
            '&columns[0][data]=artist'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=Genesis')

    def test(self):
        self.assertEqual(self.response.status_code, 400)
        self.assertEqual(
            self.response.json()['data'],
            {'artist': [
                'Select a valid choice. '
                'That choice is not one of the available choices.']})


class AlbumFilter(DatatablesFilterSet):
    """Filter name, artist and genre by name with icontains"""

    name = filters.CharFilter(lookup_expr='icontains')
    genres = filters.CharFilter(lookup_expr='name__icontains', distinct=True)
    artist = filters.CharFilter(lookup_expr='name__icontains')

    class Meta:
        model = Album
        fields = '__all__'


class AlbumIcontainsViewSet(AlbumFilterViewSet):
    filterset_fields = None
    filterset_class = AlbumFilter


class TestIcontainsOne(TestWithViewSet):

    def setUp(self):
        self.response = self.client.get(
            '/api/albumsi/?format=datatables&length=10'
            '&columns[0][data]=name'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=on')
        self.json = self.response.json()
        self.assertEqual(self.response.status_code, 200)

    def test(self):
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 6)


class TestIcontainsTwo(TestWithViewSet):

    def setUp(self):
        self.response = self.client.get(
            '/api/albumsi/?format=datatables&length=10'
            '&columns[0][data]=name'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=on'
            '&columns[1][data]=genres'
            '&columns[1][searchable]=true'
            '&columns[1][search][value]=blues')
        self.json = self.response.json()
        self.assertEqual(self.response.status_code, 200)

    def test(self):
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 2)


class TestOrder(TestWithViewSet):
    def setUp(self):
        self.response = self.client.get(
            '/api/albumsi/?format=datatables&length=10'
            '&columns[0][data]=artist_name'
            '&columns[0][name]=artist__name'
            '&columns[0][orderable]=true'
            '&order[0][column]=0'
            '&order[0][dir]=desc')
        self.json = self.response.json()
        self.assertEqual(self.response.status_code, 200)

    def test(self):
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 15)
        self.assertEqual(self.json['data'][0]['artist_name'],
                         'The Velvet Underground')


router = routers.DefaultRouter()
router.register(r'albums', AlbumFilterViewSet)
router.register(r'albumsi', AlbumIcontainsViewSet)


urlpatterns = [
    url('^api/', include(router.urls)),
]
