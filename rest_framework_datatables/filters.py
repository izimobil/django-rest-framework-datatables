import re

from django.db.models import Q

from rest_framework.filters import BaseFilterBackend


class DatatablesFilterBackend(BaseFilterBackend):
    """
    Filter that works with datatables params.
    """
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('format') != 'datatables':
            return queryset

        # set the queryset count as an attribute of the view for later
        # TODO: find a better way than this hack
        setattr(view, '_datatables_total_count', queryset.count())

        # parse query params
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        search_value = getter('search[value]')
        search_regex = getter('search[regex]') == 'true'

        # filter queryset
        q = Q()
        for f in fields:
            if not f['searchable']:
                continue
            if search_value and search_value != 'false':
                if search_regex:
                    if self.is_valid_regex(search_value):
                        q |= Q(**{'%s__iregex' % f['name']: search_value})
                else:
                    q |= Q(**{'%s__icontains' % f['name']: search_value})
            f_search_value = f.get('search_value')
            f_search_regex = f.get('search_regex') == 'true'
            if f_search_value:
                if f_search_regex:
                    if self.is_valid_regex(f_search_value):
                        q |= Q(**{'%s__iregex' % f['name']: f_search_value})
                else:
                    q |= Q(**{'%s__icontains' % f['name']: f_search_value})
        queryset = queryset.filter(q).distinct()

        # set the queryset count as an attribute of the view for later
        # TODO: maybe find a better way than this hack ?
        setattr(view, '_datatables_filtered_count', queryset.count())

        # order queryset
        if len(ordering):
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_fields(self, getter):
        fields = []
        i = 0
        while True:
            col = 'columns[%d][%s]'
            data = getter(col % (i, 'data'))
            if data is None:
                break
            name = getter(col % (i, 'name'))
            if not name:
                name = data
            search_col = col % (i, 'search')
            field = {
                'name': name.replace('.', '__'),
                'data': data,
                'searchable': getter(col % (i, 'searchable')) == 'true',
                'orderable': getter(col % (i, 'orderable')) == 'true',
                'search_value': getter('%s[%s]' % (search_col, 'value')),
                'search_regex': getter('%s[%s]' % (search_col, 'regex')),
            }
            fields.append(field)
            i += 1
        return fields

    def get_ordering(self, getter, fields):
        ordering = []
        i = 0
        while True:
            col = 'order[%d][%s]'
            idx = getter(col % (i, 'column'))
            if idx is None:
                break
            try:
                field = fields[int(idx)]
            except IndexError:
                i += 1
                continue
            if not field['orderable']:
                i += 1
                continue
            dir_ = getter(col % (i, 'dir'), 'asc')
            ordering.append('%s%s' % (
                '-' if dir_ == 'desc' else '',
                field['name']
            ))
            i += 1
        return ordering

    def is_valid_regex(cls, regex):
        try:
            re.compile(regex)
            return True
        except re.error:
            return False
