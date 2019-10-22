import re
from functools import reduce
from copy import deepcopy
import operator

from django.db.models import Q

from rest_framework.filters import BaseFilterBackend


class DatatablesBaseFilterBackend(BaseFilterBackend):
    """Base class for definining your own DatatablesFilterBackend classes"""

    def get_query_data(self, request):
        ret = {}
        ret['fields'] = self.get_fields(request)
        ret['ordering'] = self.get_ordering(request)
        ret['search_value'] = request.query_params.get('search[value]')
        ret['search_regex'] = (request.query_params.get('search[regex]')
                               == 'true')
        return ret

    def get_fields(self, request):
        getter = request.query_params.get
        fields = []
        i = 0
        while True:
            col = 'columns[%d][%s]'
            data = getter(col % (i, 'data'))
            # break out only when there are no more
            # fields to get.
            if data is None:
                break
            name = getter(col % (i, 'name'))
            if not name:
                name = data
            search_col = col % (i, 'search')
            # to be able to search across multiple fields (e.g. to search
            # through concatenated names), we create a list of the name field,
            # replacing dot notation with double-underscores and splitting
            # along the commas.
            field = {
                'name': [
                    n.lstrip() for n in name.replace('.', '__').split(',')
                ],
                'data': data,
                'searchable': getter(col % (i, 'searchable')) == 'true',
                'orderable': getter(col % (i, 'orderable')) == 'true',
                'search_value': getter('%s[%s]' % (search_col, 'value')),
                'search_regex': getter('%s[%s]' % (search_col, 'regex')),
            }
            fields.append(field)
            i += 1
        return fields

    def get_ordering(self, request):
        getter = request.query_params.get
        fields = self.get_fields(request)
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
                field['name'][0]
            ))
            i += 1
        return ordering

    def is_valid_regex(cls, regex):
        try:
            re.compile(regex)
            return True
        except re.error:
            return False


class DatatablesFilterBackend(DatatablesBaseFilterBackend):
    """
    Filter that works with datatables params.
    """
    def filter_queryset(self, request, queryset, view):
        if request.accepted_renderer.format != 'datatables':
            return queryset

        filtered_count_before = queryset.count()
        total_count = view.get_queryset().count()
        # set the queryset count as an attribute of the view for later
        # TODO: find a better way than this hack
        setattr(view, '_datatables_total_count', total_count)

        # parse query params
        query_data = self.get_query_data(request)
        fields = query_data['fields']
        ordering = query_data['ordering']
        search_value = query_data['search_value']
        search_regex = query_data['search_regex']

        # filter queryset
        q = Q()
        for f in fields:
            if not f['searchable']:
                continue
            q |= self.f_search_q(f, search_value, search_regex)
            f_search_value = f.get('search_value')
            f_search_regex = f.get('search_regex') == 'true'
            q &= self.f_search_q(f, f_search_value, f_search_regex)
        if q:
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = filtered_count_before
        # set the queryset count as an attribute of the view for later
        # TODO: maybe find a better way than this hack ?
        setattr(view, '_datatables_filtered_count', filtered_count)

        # order queryset
        if len(ordering):
            if hasattr(view, 'datatables_additional_order_by'):
                additional = view.datatables_additional_order_by
                # Django will actually only take the first occurrence if the
                # same column is added multiple times in an order_by, but it
                # feels cleaner to double check for duplicate anyway.
                if not any((o[1:] if o[0] == '-' else o) == additional
                           for o in ordering):
                    ordering.append(additional)

            queryset = queryset.order_by(*ordering)
        return queryset

    def f_search_q(self, f, search_value, search_regex=False):
        qs = []
        if search_value and search_value != 'false':
            if search_regex:
                if self.is_valid_regex(search_value):
                    for x in f['name']:
                        qs.append(Q(**{'%s__iregex' % x: search_value}))
            else:
                for x in f['name']:
                    qs.append(Q(**{'%s__icontains' % x: search_value}))
        return reduce(operator.or_, qs, Q())
