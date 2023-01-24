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
        self.assertEqual(content, bytes())

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
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

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
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

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
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

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
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

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
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

    def test_render_extra_json(self):
        class TestAPIView(APIView):
            def test_callback(self):
                return "key", "value"

            class Meta:
                datatables_extra_json = ('test_callback', )
        obj = {'recordsTotal': 4, 'recordsFiltered': 2, 'data': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = TestAPIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=2')
        )
        content = renderer.render(obj, 'application/json', {'request': request, 'view': view})
        expected = {
            'recordsTotal': 4,
            'recordsFiltered': 2,
            'data': [{'foo': 'bar'}, {'spam': 'eggs'}],
            'key': 'value',
            'draw': 2
        }
        self.assertEqual(json.loads(content.decode('utf-8')), expected)

    def test_render_extra_json_attr_missing(self):
        class TestAPIView(APIView):
            class Meta:
                datatables_extra_json = ('test_callback', )

        obj = {'recordsTotal': 4, 'recordsFiltered': 2, 'data': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = TestAPIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=2')
        )
        try:
            renderer.render(obj, 'application/json', {'request': request, 'view': view})
            self.assertEqual(True, False, "TypeError expected; did not occur.")
        except TypeError as e:
            self.assertEqual(e.__str__(), "extra_json_funcs: test_callback not a view method.")

    def test_render_extra_json_attr_not_callable(self):
        class TestAPIView(APIView):
            test_callback = 'gotcha'
            class Meta:
                datatables_extra_json = ('test_callback', )

        obj = {'recordsTotal': 4, 'recordsFiltered': 2, 'data': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = TestAPIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=2')
        )
        try:
            renderer.render(obj, 'application/json', {'request': request, 'view': view})
            self.assertEqual(True, False, "TypeError expected; did not occur.")
        except TypeError as e:
            self.assertEqual(e.__str__(), "extra_json_funcs: test_callback not callable.")

    def test_render_extra_json_clashes(self):
        class TestAPIView(APIView):
            def test_callback(self):
                return "recordsTotal", "this could be bad"

            class Meta:
                datatables_extra_json = ('test_callback', )

        obj = {'recordsTotal': 4, 'recordsFiltered': 2, 'data': [{'foo': 'bar'}, {'spam': 'eggs'}]}
        renderer = DatatablesRenderer()
        view = TestAPIView()
        request = view.initialize_request(
            self.factory.get('/api/foo/?format=datatables&draw=2')
        )
        try:
            renderer.render(obj, 'application/json', {'request': request, 'view': view})
            self.assertEqual(True, False, "Value expected; did not occur.")
        except ValueError as e:
            self.assertEqual(e.__str__(), "Duplicate key found: recordsTotal")
