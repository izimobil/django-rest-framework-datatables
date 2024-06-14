from unittest import mock, SkipTest

from django.urls import include, path
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
    from rest_framework_datatables.django_filters.filters import (
        GlobalFilter)
except ImportError:
    raise SkipTest('django-filter not available')


factory = APIRequestFactory()


class CustomDatatablesFilterBackend(DatatablesFilterBackend):
    """
    Override before and after counts to demonstrate performance fix.
    """

    def get_queryset_count_before(self, queryset):
        return 999

    def get_queryset_count_after(self, queryset):
        return 99


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


class CustomBackendAlbumFilterViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [CustomDatatablesFilterBackend]
    filterset_fields = '__all__'


@override_settings(ROOT_URLCONF=__name__)
class TestWithViewSet(TestDFBackendTestCase):

    def setUp(self):
        self.client = APIClient()




class TestUnfiltered(TestWithViewSet):

    def setUp(self):
        self.response = self.client.get('/api/albums/?format=datatables&length=-1')
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


class TestCustomFiltered(TestWithViewSet):
    fixtures = ['test_data']
    backend = CustomDatatablesFilterBackend()


    def setUp(self):
        self.response = self.client.get(
            '/api/albumsc/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=1971')
        self.json = self.response.json()

    def test_count_before(self):
        self.assertEqual(self.json['recordsTotal'], 999)

    def test_count_after(self):
        self.assertEqual(self.json['recordsFiltered'], 99)


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
            '&columns[0][search][value]=Genesis'
            '&columns[1][data]=')

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
            '&columns[0][data]=artist'
            '&columns[0][name]=irrelevant'
            '&columns[0][orderable]=true'
            '&order[0][column]=0'
            '&order[0][dir]=desc')
        self.json = self.response.json()
        self.assertEqual(self.response.status_code, 200)

    def test(self):
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 15)
        self.assertEqual(self.json['data'][0]['artist']['name'],
                         'The Velvet Underground')


class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class AlbumGlobalFilter(AlbumFilter):
    """Filter name, artist and genre by name with icontains"""

    name = GlobalCharFilter(lookup_expr='icontains')
    genres = GlobalCharFilter(field_name='genres__name', lookup_expr='icontains')
    artist = GlobalCharFilter(field_name='artist__name', lookup_expr='icontains')
    year = GlobalCharFilter()

    class Meta:
        model = Album
        fields = '__all__'


class AlbumGlobalViewSet(AlbumIcontainsViewSet):
    filterset_class = AlbumGlobalFilter


class TestGlobal(TestWithViewSet):
    """Test global searches.

    Tests if the backend will automatically respect global search
    queries and combine them with column searches in a meaningful
    manner.

    """

    def search(self, url):
        self.response = self.client.get(url)
        self.json = self.response.json()
        self.data = self.json['data']

    def test_simple_global(self):
        self.search(
            '/api/albumsg/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&search[value]=1971')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 1)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data[0]['year'], 1971)

    def test_combined_global(self):
        self.search(
            '/api/albumsg/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&columns[0][search][value]=1966'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&search[value]=l')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 2)
        self.assertEqual(len(self.data), 2)
        self.assertEqual(self.data[0]['name'], 'Blonde on Blonde')
        self.assertEqual(self.data[1]['name'], 'Revolver')

    def test_combined_global_distinct(self):
        self.search(
            '/api/albumsg/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&columns[1][search][value]=i'
            '&columns[2][data]=artist'
            '&columns[2][searchable]=true'
            '&columns[2][search][value]=a'
            # 5 matches up to here
            '&columns[3][data]=genres'
            '&columns[3][searchable]=true'
            # global search finds a match in one album title and one
            # genre name
            '&search[value]=Blue')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 2)
        self.assertEqual(len(self.data), 2)
        self.assertEqual(self.data[0]['name'], 'Highway 61 Revisited')
        self.assertEqual(self.data[0]['genres'], 'Blues Rock, Folk Rock')
        self.assertEqual(self.data[1]['name'], 'Kind of Blue')
        self.assertEqual(self.data[1]['genres'], 'Modal')

    def test_combined_global_regex_distinct(self):
        self.search(
            '/api/albumsg/?format=datatables&length=10'
            '&columns[0][data]=year'
            '&columns[0][searchable]=true'
            '&columns[1][data]=name'
            '&columns[1][searchable]=true'
            '&columns[2][data]=artist'
            '&columns[2][searchable]=true'
            '&columns[3][data]=genres'
            '&columns[3][searchable]=true'
            '&search[value]=^High.*61.*d$'
            '&search[regex]=true')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.json['recordsTotal'], 15)
        self.assertEqual(self.json['recordsFiltered'], 1)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data[0]['name'], 'Highway 61 Revisited')
        self.assertEqual(self.data[0]['genres'], 'Blues Rock, Folk Rock')


router = routers.DefaultRouter()
router.register(r'albums', AlbumFilterViewSet, basename="albums")
router.register(r'albumsc', CustomBackendAlbumFilterViewSet, basename="albumsc")
router.register(r'albumsi', AlbumIcontainsViewSet, basename="albumsi")
router.register(r'albumsg', AlbumGlobalViewSet, basename="albumsg")


urlpatterns = [
    path('api/', include(router.urls)),
]
