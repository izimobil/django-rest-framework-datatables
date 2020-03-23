import re
from functools import reduce
import operator

from django.db.models import Q

from rest_framework.filters import BaseFilterBackend


def is_valid_regex(regex):
    """helper function that checks regex for validity"""
    try:
        re.compile(regex)
        return True
    except re.error:
        return False


def f_search_q(f, search_value, search_regex=False):
    """helper function that returns a Q-object for a search value"""
    qs = []
    if search_value and search_value != 'false':
        if search_regex:
            if is_valid_regex(search_value):
                for x in f['name']:
                    qs.append(Q(**{'%s__iregex' % x: search_value}))
        else:
            for x in f['name']:
                qs.append(Q(**{'%s__icontains' % x: search_value}))
    return reduce(operator.or_, qs, Q())


class DatatablesBaseFilterBackend(BaseFilterBackend):
    """Base class for definining your own DatatablesFilterBackend classes"""

    def check_renderer_format(self, request):
        return request.accepted_renderer.format == 'datatables'

    def parse_datatables_query(self, request, view):
        """parse request.query_params into a list of fields and orderings and
        global search parameters (value and regex)"""
        ret = {}
        ret['fields'] = self.get_fields(request)
        ret['search_value'] = request.query_params.get('search[value]')
        ret['search_regex'] = (request.query_params.get('search[regex]')
                               == 'true')
        return ret

    def get_fields(self, request):
        """called by parse_query_params to get the list of fields"""
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
                'search_regex': (getter('%s[%s]' % (search_col, 'regex'))
                                 == 'true'),
            }
            fields.append(field)
            i += 1
        return fields

    def get_ordering_fields(self, request, view, fields):
        """called by parse_query_params to get the ordering

        return value must be a list of tuples.
        (field, dir)

        field is the field to order by and dir is the direction of the
        ordering ('asc' or 'desc').

        """
        getter = request.query_params.get
        ret = []
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
            ret.append((field, dir_))
            i += 1
        return ret

    def set_count_before(self, view, total_count):
        # set the queryset count as an attribute of the view for later
        # TODO: find a better way than this hack
        setattr(view, '_datatables_total_count', total_count)

    def set_count_after(self, view, filtered_count):
        """called by filter_queryset to store the ordering after the filter
        operations

        """
        # set the queryset count as an attribute of the view for later
        # TODO: maybe find a better way than this hack ?
        setattr(view, '_datatables_filtered_count', filtered_count)


class DatatablesFilterBackend(DatatablesBaseFilterBackend):
    """
    Filter that works with datatables params.
    """
    def filter_queryset(self, request, queryset, view):
        """filter the queryset

        subclasses overriding this method should make sure to do all
        necessary steps

        -  Return unfiltered queryset if accepted renderer format is
           not 'datatables' (via `check_renderer_format`)

        - store the counts before and after filtering with
          `set_count_before` and `set_count_after`

        - respect ordering (in `ordering` key of parsed datatables
          query)

        """
        if not self.check_renderer_format(request):
            return queryset

        self.set_count_before(view, view.get_queryset().count())

        datatables_query = self.parse_datatables_query(request, view)

        q = self.get_q(datatables_query)
        if q:
            queryset = queryset.filter(q).distinct()
        self.set_count_after(view, queryset.count())

        queryset = queryset.order_by(
            *self.get_ordering(request, view, datatables_query['fields']))
        return queryset

    def get_q(self, datatables_query):
        q = Q()
        for f in datatables_query['fields']:
            if not f['searchable']:
                continue
            q |= f_search_q(f,
                            datatables_query['search_value'],
                            datatables_query['search_regex'])
            q &= f_search_q(f,
                            f.get('search_value'),
                            f.get('search_regex', False))
        return q

    def get_ordering(self, request, view, fields):
        """called by parse_query_params to get the ordering

        return value must be a valid list of arguments for order_by on
        a queryset

        """
        ordering = []
        for field, dir_ in self.get_ordering_fields(request, view, fields):
            ordering.append('%s%s' % (
                '-' if dir_ == 'desc' else '',
                field['name'][0]
            ))
        if len(ordering):
            if hasattr(view, 'datatables_additional_order_by'):
                additional = view.datatables_additional_order_by
                # Django will actually only take the first occurrence if the
                # same column is added multiple times in an order_by, but it
                # feels cleaner to double check for duplicate anyway.
                if not any((o[1:] if o[0] == '-' else o) == additional
                           for o in ordering):
                    ordering.append(additional)
        return ordering
