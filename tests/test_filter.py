from albums.models import Album
from albums.serializers import AlbumSerializer

from django.conf.urls import url
from django.test.utils import override_settings
from django.test import TestCase

from rest_framework.generics import ListAPIView
from rest_framework.test import (
    APIClient,
)
from rest_framework_datatables.pagination import (
    DatatablesLimitOffsetPagination,
)

class TestFilterTestCase(TestCase):
    class TestAPIView(ListAPIView):
        serializer_class = AlbumSerializer
        pagination_class = DatatablesLimitOffsetPagination
        datatables_additional_order_by = 'year'

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
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)


urlpatterns = [
    url('^api/additionalorderby', TestFilterTestCase.TestAPIView.as_view()),
]
