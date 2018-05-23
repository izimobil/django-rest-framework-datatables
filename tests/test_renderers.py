import unittest
import json

from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework_datatables.renderers import DatatablesRenderer


class DatatablesRendererTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_render_no_data(self):
        renderer = DatatablesRenderer()
        content = renderer.render(None)
        self.assertEquals(content, bytes())

    def test_render_no_pagination1(self):
        obj = [{'foo': 'bar'}]
        renderer = DatatablesRenderer()
        view = APIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=1')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 1,
            'recordsFiltered': 1,
            'data': [{'foo': 'bar'}],
            'draw': 1
        }
        self.assertEquals(json.loads(content.decode('utf-8')), expected)

    def test_render_no_pagination1_1(self):
        obj = [{'foo': 'bar'}]
        renderer = DatatablesRenderer()
        view = APIView()
        request = view.initialize_request(
            self.factory.get('/api/foo.datatables?draw=1')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 1,
            'recordsFiltered': 1,
            'data': [{'foo': 'bar'}],
            'draw': 1
        }
        self.assertEquals(json.loads(content.decode('utf-8')), expected)

    def test_render_no_pagination2(self):
        obj = {'results': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = APIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=1')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 2,
            'recordsFiltered': 2,
            'data': [{'foo': 'bar'}, {'spam': 'eggs'}],
            'draw': 1
        }
        self.assertEquals(json.loads(content.decode('utf-8')), expected)

    def test_render_no_pagination3(self):
        obj = {'results': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = APIView()
        view._datatables_total_count = 4
        view._datatables_filtered_count = 2
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=1')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 4,
            'recordsFiltered': 2,
            'data': [{'foo': 'bar'}, {'spam': 'eggs'}],
            'draw': 1
        }
        self.assertEquals(json.loads(content.decode('utf-8')), expected)

    def test_render(self):
        obj = {'recordsTotal': 4, 'recordsFiltered': 2, 'data': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = APIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=2')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 4,
            'recordsFiltered': 2,
            'data': [{'foo': 'bar'}, {'spam': 'eggs'}],
            'draw': 2
        }
        self.assertEquals(json.loads(content.decode('utf-8')), expected)
