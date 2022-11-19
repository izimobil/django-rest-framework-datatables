from django.test import TestCase, override_settings, modify_settings
from django.conf import settings
from django.urls import path

from rest_framework.test import APIClient
from rest_framework.settings import api_settings

from rest_framework_datatables.pagination import (
    DatatablesLimitOffsetPagination, DatatablesPageNumberPagination, DatatablesOnlyPageNumberPagination
)
from rest_framework.generics import ListAPIView

from albums.views import AlbumViewSet
from albums.models import Album
from albums.serializers import AlbumSerializer


class AlbumPostListAPIView(ListAPIView):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all().order_by('rank')

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DatatablesPageNumberPaginationCustomMax(DatatablesPageNumberPagination):
    max_page_size = 15


class DatatablesLimitOffsetPaginationCustomMax(DatatablesLimitOffsetPagination):
    max_limit = 15


class DatatablesOnlyPageNumberPaginationCustomMax(DatatablesOnlyPageNumberPagination):
    max_page_size = 15


class TestApiTestCase(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.client = APIClient()
        AlbumViewSet.pagination_class = DatatablesPageNumberPagination

    def test_no_datatables(self):
        response = self.client.get('/api/albums/')
        expected = 15
        result = response.json()
        self.assertEqual(result['count'], expected)

    def test_datatables_query(self):
        response = self.client.get('/api/albums/?format=datatables')
        expected = 15
        result = response.json()
        self.assertEqual('count' in result, False)
        self.assertEqual('recordsTotal' in result, True)
        self.assertEqual(result['recordsTotal'], expected)

    @override_settings(ROOT_URLCONF=__name__)
    def test_post_request(self):
        response = self.client.post(
            '/api/post/albums/?format=datatables&keep=name',
            {
                'length': '10',
                'columns[0][data]': 'artist_name',
                'columns[0][name]': 'artist__name',
                'columns[0][orderable]': 'true',
                'order[0][column]': '0',
                'order[0][dir]': 'desc',
            }
        )
        expected = (15, 15, 'The Velvet Underground')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)
        self.assertEqual((result['data'][0]['name']), 'The Velvet Underground & Nico')

    def test_datatables_suffix(self):
        response = self.client.get('/api/albums.datatables/')
        expected = 15
        result = response.json()
        self.assertEqual('count' in result, False)
        self.assertEqual('recordsTotal' in result, True)
        self.assertEqual(result['recordsTotal'], expected)

    def test_pagenumber_pagination(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 5, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)

    def test_pagenumber_pagination_show_all(self):
        response = self.client.get('/api/albums/?format=datatables&length=-1&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)

    def test_pagenumber_pagination_invalid_page1(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=20&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        self.assertEqual(response.status_code, 404)

    def test_pagenumber_pagination_invalid_page2(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=abc&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        self.assertEqual(response.status_code, 404)

    def test_pagenumber_pagination_invalid_page_size1(self):
        response = self.client.get('/api/albums/?format=datatables&length=abc&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 5, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)

    def test_pagenumber_pagination_invalid_page_size2(self):
        response = self.client.get('/api/albums/?format=datatables&length=-999&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 5, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': __name__ + '.DatatablesPageNumberPaginationCustomMax',
    })
    def test_pagenumber_pagination_invalid_max(self):
        AlbumViewSet.pagination_class = DatatablesPageNumberPaginationCustomMax
        response = self.client.get('/api/albums/?format=datatables&length=20&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_disable_pagination(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?format=datatables&start=10&columns[0][data]=name&columns[1][data]=artist_name&length=-1&draw=1')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_invalid_length1(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get(
            '/api/albums/?format=datatables&length=abc&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_invalid_length2(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get(
            '/api/albums/?format=datatables&length=-999&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_invalid_start1(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get(
            '/api/albums/?format=datatables&length=10&start=abc&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_invalid_start2(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get(
            '/api/albums/?format=datatables&length=10&start=-999&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': __name__ + '.DatatablesLimitOffsetPaginationCustomMax',
    })
    def test_limitoffset_pagination_invalid_max(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPaginationCustomMax
        client = APIClient()
        response = client.get(
            '/api/albums/?format=datatables&length=20&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
    })
    def test_limitoffset_pagination_no_datatables(self):
        AlbumViewSet.pagination_class = DatatablesLimitOffsetPagination
        client = APIClient()
        response = client.get('/api/albums/?limit=10&offset=10')
        expected = (15, 'Elvis Presley')
        result = response.json()
        self.assertEqual((result['count'], result['results'][0]['artist_name']), expected)

    def test_column_column_data_null(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&start=10&columns[0][data]=&columns[1][data]=name')
        expected = (15, 15, 'The Sun Sessions')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

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

    def test_param_keep_field(self):
        response = self.client.get(
            '/api/albums/?format=datatables&length=10&columns[0][data]=artist.name&columns[0][name]=artist.name&keep=year')
        expected = (15, 15, 1967)
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['year']), expected)

    def test_param_keep_field_search(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist.name&columns[0][name]=artist.name,year&columns[0][searchable]=true&keep=year&search[value]=1968')
        expected = (1, 15, 'The Beatles', 1968)
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist']['name'], result['data'][0]['year']), expected)

    def test_dt_force_serialize_generic(self):
        response = self.client.get('/api/artists/?format=datatables&length=10&start=0&columns[0][data]=&columns[1][data]=name')
        result = response.json()
        self.assertTrue('id' in result['data'][0])

    def test_filtering_simple(self):
        response = self.client.get('/api/albums/?format=datatables&columns[0][data]=name&columns[0][searchable]=true&columns[1][data]=artist__name&columns[1][searchable]=true&search[value]=are+you+exp')
        expected = (1, 15, 'Are You Experienced')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_multiple_names(self):
        # Two asserts here to test searching on separate namespaces.
        api_call = '/api/albums/?format=datatables&columns[0][data]=name&columns[0][searchable]=true&columns[1][data]=artist__name&columns[1][name]=artist__name,year&columns[1][searchable]=true'
        # First search.
        response_1 = self.client.get(api_call + '&search[value]=Beatles')
        # Second search.
        response_2 = self.client.get(api_call + '&search[value]=1968')
        expected_1 = (5, 15, 'Sgt. Pepper\'s Lonely Hearts Club Band')
        expected_2 = (1, 15, 'The Beatles ("The White Album")')
        result_1 = response_1.json()
        result_2 = response_2.json()
        self.assertEqual((result_1['recordsFiltered'], result_1['recordsTotal'], result_1['data'][0]['name']), expected_1)
        self.assertEqual((result_2['recordsFiltered'], result_2['recordsTotal'], result_2['data'][0]['name']), expected_2)

    def test_filtering_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[regex]=true&search[value]=^Highway [0-9]{2} Revisited$')
        expected = (1, 15, 'Highway 61 Revisited')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_bad_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=name&columns[0][searchable]=true&search[regex]=true&search[value]=^Highway [0')
        expected = (15, 15, 'Sgt. Pepper\'s Lonely Hearts Club Band')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['name']), expected)

    def test_filtering_foreignkey_without_nested_serializer(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&search[value]=Jimi')
        expected = (1, 15, 'The Jimi Hendrix Experience')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_foreignkey_with_nested_serializer(self):
        response = self.client.get(
            '/api/albums/?format=datatables&length=10&columns[0][data]=artist.name&columns[0][name]=artist.name&columns[0][searchable]=true&search[value]=Jimi')
        expected = (1, 15, 'The Jimi Hendrix Experience')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist']['name']), expected)

    def test_filtering_column(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][value]=Beatles')
        expected = (5, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_column_suffix(self):
        response = self.client.get('/api/albums.datatables?length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][value]=Beatles')
        expected = (5, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_column_regex(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][regex]=true&columns[0][search][value]=^bob')
        expected = (2, 15, 'Bob Dylan')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_multicolumn1(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][value]=Beatles&columns[1][data]=year&columns[1][searchable]=true&columns[1][search][value]=1968')
        expected = (1, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_filtering_multicolumn2(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][searchable]=true&columns[0][search][value]=Beatles&columns[1][data]=year&columns[1][searchable]=true&columns[1][search][value]=2018')
        expected = (0, 15)
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal']), expected)

    def test_ordering_simple(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=true&order[0][column]=0&order[0][dir]=desc')
        expected = (15, 15, 'The Velvet Underground')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_ordering_but_not_orderable(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=false&order[0][column]=0&order[0][dir]=desc')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    def test_ordering_bad_column_index(self):
        response = self.client.get('/api/albums/?format=datatables&length=10&columns[0][data]=artist_name&columns[0][name]=artist__name&columns[0][orderable]=true&order[0][column]=8&order[0][dir]=desc')
        expected = (15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], result['data'][0]['artist_name']), expected)

    @override_settings(REST_FRAMEWORK={
        'DEFAULT_PAGINATION_CLASS': __name__ + '.DatatablesOnlyPageNumberPaginationCustomMax',
    })
    def test_datatables_only_pagination_no_datatables(self):
        AlbumViewSet.pagination_class = DatatablesOnlyPageNumberPaginationCustomMax
        response = self.client.get('/api/albums/')
        expected = (list, 15)
        result = response.json()
        self.assertEqual((type(result), len(result)), expected)

    def test_datatables_only_pagination_with_datatables(self):
        AlbumViewSet.pagination_class = DatatablesOnlyPageNumberPaginationCustomMax
        response = self.client.get('/api/albums/?format=datatables&length=20&start=10&columns[0][data]=name&columns[1][data]=artist_name&draw=1')
        expected = (15, 15, 15, 'The Beatles')
        result = response.json()
        self.assertEqual((result['recordsFiltered'], result['recordsTotal'], len(result['data']), result['data'][0]['artist_name']), expected)


urlpatterns = [
    path('api/post/albums/', AlbumPostListAPIView.as_view()),
]
