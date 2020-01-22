import sys
from unittest import SkipTest

from django.conf.urls import include, url
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework import routers, viewsets
from rest_framework.test import APIClient, APIRequestFactory

from albums.models import Album
from albums.serializers import AlbumSerializer

if sys.version_info < (3, ):
    raise SkipTest('Python <3 is not supported, skipping module')
else:
    from unittest import mock

try:
    from django_filters import rest_framework as filters
    from rest_framework_datatables.django_filters.backends import (
        DatatablesFilterBackend)
except ImportError:
    raise SkipTest('django_filter not available, skipping module')


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
        assert res == qs


class AlbumFilter(filters.FilterSet):

    class Meta:
        model = Album
        fields = '__all__'


# Most things are much easier to test with client and viewset, even
# though we're testing the backend here
class AlbumFilterViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [DatatablesFilterBackend]


@override_settings(ROOT_URLCONF=__name__)
class TestWithViewSet(TestDFBackendTestCase):

    def setUp(self):
        self.client = APIClient()


router = routers.DefaultRouter()
router.register(r'albums', AlbumFilterViewSet)


urlpatterns = [
    url('^api/', include(router.urls)),
]


class TestUnfiltered(TestWithViewSet):

    def setUp(self):
        self.result = self.client.get('/api/albums/?format=datatables')


class TestCount(TestUnfiltered):

    def test_count_before(self):
        assert [self.result.renderer_context.get('view')
                ._datatables_total_count
                == 15]

    def test_count_after(self):
        assert (self.result.renderer_context.get('view')
                ._datatables_filtered_count
                == 15)
