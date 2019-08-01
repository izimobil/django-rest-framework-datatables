from django.db.models import Q
from django.test import TestCase
from rest_framework.test import APIClient

from albums.models import Album
from albums.views import AlbumViewSet
from rest_framework_datatables.pagination import (
    DatatablesPageNumberPagination
)


class DatatablesEditorTestCase(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.client = APIClient()
        AlbumViewSet.pagination_class = DatatablesPageNumberPagination

    def test_edit_one(self):
        data = {
            'action': 'edit',
            'data[1][artist][id]': 2,
            'data[1][name]': 'New name1',
        }
        response = self.client.post('/api/albums/editor/', data)
        result = response.json()['data']
        self.assertEqual(result[0]['name'], 'New name1')
        self.assertEqual(result[0]['artist']['id'], 2)
        album = Album.objects.get(pk=1)
        self.assertEqual([album.name, album.artist.id], ['New name1', 2])

    def test_edit_two(self):
        data = {
            'action': 'edit',
            'data[1][artist][id]': 2,
            'data[1][name]': 'New name1',
            'data[4][artist][id]': 4,
            'data[4][name]': 'New name4',
        }
        response = self.client.post('/api/albums/editor/', data)
        result = response.json()['data']
        order_flag = 0 if result[0]['name'] == 'New name1' else 1

        self.assertEqual(result[order_flag-0]['name'], 'New name1')
        self.assertEqual(result[order_flag-0]['artist']['id'], 2)
        album = Album.objects.get(pk=1)
        self.assertEqual([album.name, album.artist.id], ['New name1', 2])

        self.assertEqual(result[order_flag-1]['name'], 'New name4')
        self.assertEqual(result[order_flag-1]['artist']['id'], 4)
        album = Album.objects.get(pk=4)
        self.assertEqual([album.name, album.artist.id], ['New name4', 4])

    def test_edit_wrong_foreignkey(self):
        data = {
            'action': 'edit',
            'data[1][artist][id]': 1,
            'data[1][name]': 'New name1',
        }
        response = self.client.post('/api/albums/editor/', data)
        self.assertEquals(response.status_code, 404)

    def test_edit_wrong_id(self):
        data = {
            'action': 'edit',
            'data[20][rank]': 3,
            'data[20][artist][id]': 2,
            'data[20][name]': 'New name',
            'data[20][year]': 1955
        }
        response = self.client.post('/api/albums/editor/', data)
        expected = {'detail': 'Not found.'}
        result = response.json()
        self.assertEqual(result, expected)

    def test_remove_one(self):
        data = {
            'action': 'remove',
            'data[7][rank]': '',
            'data[7][DT_RowId]': '7',
            'data[7][DT_RowAttr][data-pk]': '7',
        }
        response = self.client.post('/api/albums/editor/', data)
        expected = {'data': []}
        result = response.json()
        self.assertEqual(result, expected)
        self.assertQuerysetEqual(Album.objects.filter(pk=7), [])
        self.assertEqual(Album.objects.all().count(), 14)

    def test_remove_two(self):
        data = {
            'action': 'remove',
            'data[7][rank]': '',
            'data[8][rank]': '',
        }
        response = self.client.post('/api/albums/editor/', data)
        expected = {'data': []}
        result = response.json()
        self.assertEqual(result, expected)
        self.assertQuerysetEqual(Album.objects.filter(Q(pk=7) | Q(pk=8)), [])
        self.assertEqual(Album.objects.all().count(), 13)

    def test_create(self):
        data = {
            'action': 'create',
            'data[0][rank]': 16,
            'data[0][artist][id]': 2,
            'data[0][name]': 'New name',
            'data[0][year]': 1950,
        }
        response = self.client.post('/api/albums/editor/', data)
        result = response.json()['data'][0]
        self.assertEqual(result['name'], 'New name')
        self.assertEqual(result['artist']['id'], 2)
        self.assertEqual(result['DT_RowId'], 16)
        album = Album.objects.get(pk=16)
        self.assertEqual([album.name, album.artist.id], ['New name', 2])

    def test_create_wrong_foreignkey(self):
        data = {
            'action': 'create',
            'data[0][rank]': 16,
            'data[0][artist][id]': 1,
            'data[0][name]': 'New name',
            'data[0][year]': 1950,
        }
        response = self.client.post('/api/albums/editor/', data)
        self.assertEquals(response.status_code, 404)
        self.assertEqual(Album.objects.all().count(), 15)

    def test_one_wrong_field_name(self):
        data = {
            'action': 'create',
            'data[0][incorrect_field]': 16,
            'data[0][artist][id]': 2,
            'data[0][name]': 'New name',
            'data[0][year]': 1950,
        }
        response = self.client.post('/api/albums/editor/', data)
        self.assertEquals(response.status_code, 400)
        result = response.json()[0]
        expected = 'The following fields are present in the request, but they are not writable: incorrect_field'
        self.assertEqual(result, expected)

    def test_two_wrong_field_name(self):
        data = {
            'action': 'create',
            'data[0][incorrect_field1]': 16,
            'data[0][incorrect_field2]': 16,
        }
        response = self.client.post('/api/albums/editor/', data)
        expected1 = 'The following fields are present in the request, but they are not writable:'
        expected2 = 'incorrect_field1'
        expected3 = 'incorrect_field2'
        self.assertContains(response, expected1, count=1, status_code=400)
        self.assertContains(response, expected2, count=1, status_code=400)
        self.assertContains(response, expected3, count=1, status_code=400)
