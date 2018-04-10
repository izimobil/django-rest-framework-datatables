from rest_framework.serializers import (
    ModelSerializer, HyperlinkedModelSerializer
)


class FieldsFromQueryStringMixin(object):
    def filter_fields(self):
        request = self.context['request']
        if request.query_params.get('format') != 'datatables':
            return
        fields = []
        i = 0
        while True:
            field = request.query_params.get('columns[%d][data]' % i)
            if field is None:
                break
            fields.append(field)
            i += 1
        if len(fields):
            keys = set(self.fields.keys())
            for k in keys:
                if k not in fields:
                    self.fields.pop(k)


class DatatablesModelSerializer(FieldsFromQueryStringMixin, ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(DatatablesModelSerializer, self).__init__(*args, **kwargs)
        self.filter_fields()


class DatatablesHyperlinkedModelSerializer(FieldsFromQueryStringMixin,
                                           HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(DatatablesHyperlinkedModelSerializer, self).__init__(
            *args, **kwargs
        )
        self.filter_fields()
