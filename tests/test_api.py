from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework.settings import api_settings

from rest_framework_datatables.pagination import (
    DatatablesLimitOffsetPagination, DatatablesPageNumberPagination
)
from albums.views import AlbumViewSet
from albums.serializers import AlbumSerializer


class TestApiTestCase(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.client = APIClient()
        AlbumViewSet.pagination_class = DatatablesPageNumberPagination

    def test_no_datatables(self):
        response = self.client.get('/api/albums/')
        expected = 15
        result = response.json()
        self.assertEquals(result['count'], expected)

    def test_pagenumber_pagination(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_pagenumber_pagination_invalid_page(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=20&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        self.assertEquals(response.status_code, 404)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_no_length(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?format=datatables&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_no_datatables(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?limit=10&offset=10')
        expected = (15, 'Elvis Presley')
        result = response.json()
        self.assertEquals((result['count'], result['results'][0]['artist_name']), expected)

    def test_column_column_data_null(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=&columns[1][data]=name')
        expected = (15, 15, 'The Sun Sessions')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_dt_row_attrs_present(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=0&columns[0][data]=&columns[1][data]=name')
        result = response.json()
        self.assertTrue('DT_RowId' in result['data'][0])
        self.assertTrue('DT_RowAttr' in result['data'][0])

    def test_dt_force_serialize_class(self):
        AlbumSerializer.Meta.datatables_always_serialize = ('year',)
        response = self.client.get('/api/albums/?format=datatables&length=10&start=0&columns[0][data]=&columns[1][data]=name')
        result = response.json()
        self.assertTrue('year' in result['data'][0])

        delattr(AlbumSerializer.Meta, 'datatables_always_serialize')

    def test_dt_force_serialize_generic(self):
        response = self.client.get('/api/artists/?format=datatables&length=10&start=0&columns[0][data]=&columns[1][data]=name')
        result = response.json()
        self.assertTrue('id' in result['data'][0])

    def test_filtering_simple(self):
        response = self.client.get('/api/albums/?format=datatables&columns[0][data]=name&columns[0][searchable]=true&search[value]=are+you+exp')
        expected = (1, 15, 'Are You Experienced')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[regex]=true&search[value]=^Highway [0-9]{2} Revisited$')
        expected = (1, 15, 'Highway 61 Revisited')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_bad_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[regex]=true&search[value]=^Highway [0')
        expected = (15, 15, 'Sgt. Pepper\'s Lonely Hearts Club Band')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_foreignkey(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&search[value]=Jimi')
        expected = (1, 15, 'The Jimi Hendrix Experience')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_column(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][value]=Beatles')
        expected = (5, 15, 'The Beatles')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_column_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][regex]=true&columns[0][search][value]=^bob')
        expected = (2, 15, 'Bob Dylan')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_ordering_simple(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=true&order[0][column]=0&order[0][dir]=desc')
        expected = (15, 15, 'The Velvet Underground')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_ordering_but_not_orderable(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=false&order[0][column]=0&order[0][dir]=desc')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_ordering_bad_column_index(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=true&order[0][column]=8&order[0][dir]=desc')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEquals((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

