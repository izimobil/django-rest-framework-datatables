import re

from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet


def check_fields(serializer, data):
    # _writable_fields
    list_fields_in_data = set(list(data.values())[0].keys())
    list_of_writable_fields = set(
        [field.field_name for field in serializer()._writable_fields]
    )
    invalid_fields = list_fields_in_data - list_of_writable_fields
    if len(invalid_fields):
        raise ValidationError(
            "The following fields are present in the request,"
            " but they are not writable: " +
            ','.join(str(field) for field in invalid_fields)
        )


class EditorModelMixin(object):

    @staticmethod
    def get_post_date(post):
        def read_date(data_in, data_out, rest_of_line):
            field_name = data_in[0]
            if not isinstance(data_out.get(field_name), dict):
                new_data_point = {}
                data_out[field_name] = new_data_point
            else:
                new_data_point = data_out[field_name]
            if len(data_in) == 2:
                new_data_point[data_in[1]] = rest_of_line
            else:
                read_date(data_in[1:], new_data_point, rest_of_line)

        data = {}
        for (line, value) in post.items():
            if line.startswith('data'):
                line_data = re.findall(r"\[([^\[\]]*)\]", line)
                read_date(line_data, data, value)
        return data

    @action(detail=False, url_name='editor', methods=['post'])
    def editor(self, request):
        post = request.POST
        act = post['action']
        data = self.get_post_date(post)

        return_data = []
        if act == 'edit' or act == 'remove' or act == 'create':
            for elem_id, changes in data.items():
                if act == 'create':
                    check_fields(self.serializer_class, data)
                    serializer = self.serializer_class(
                        data=changes,
                        context={'request': request}
                    )
                    if not serializer.is_valid():  # pragma: no cover
                        raise ValidationError(serializer.errors)
                    serializer.save()
                    return_data.append(serializer.data)
                    continue

                elem = get_object_or_404(self.queryset, pk=elem_id)
                if act == 'edit':
                    check_fields(self.serializer_class, data)
                    serializer = self.serializer_class(
                        instance=elem, data=changes,
                        partial=True, context={'request': request}
                    )
                    if not serializer.is_valid():  # pragma: no cover
                        raise ValidationError(serializer.errors)
                    serializer.save()
                    return_data.append(serializer.data)
                elif act == 'remove':
                    elem.delete()

        return JsonResponse({'data': return_data})


class DatatablesEditorModelViewSet(EditorModelMixin, ModelViewSet):
    pass
