import operator
import re
from functools import reduce

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from .utils import get_param


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


def count_rows(queryset):
    """helper function that counts the rows a queryset would return

    Counting a distinct queryset makes the database dedupe every
    selected column, joined ones included; deduping the primary key
    alone gives the same number for much less work. Querysets using
    DISTINCT ON, selecting only some columns with values() or
    values_list(), or selecting more with annotations or extra(), are
    counted as they were before, since those columns decide which rows
    are distinct.

    """
    countable_by_pk = (
        queryset.query.distinct
        and not queryset.query.distinct_fields
        and not queryset.query.values_select
        and not queryset.query.annotations
        and not queryset.query.extra
    )
    if countable_by_pk:
        return queryset.order_by().values('pk').distinct().count()
    return queryset.count()


class DatatablesBaseFilterBackend(BaseFilterBackend):
    """Base class for definining your own DatatablesFilterBackend classes"""

    def check_renderer_format(self, request):
        return request.accepted_renderer.format == 'datatables'

    def parse_datatables_query(self, request, view):
        """parse request.query_params into a list of fields and orderings and
        global search parameters (value and regex)"""
        ret = {}
        ret['fields'] = self.get_fields(request)
        ret['search_value'] = get_param(request, 'search[value]')
        ret['search_regex'] = get_param(request, 'search[regex]') == 'true'
        return ret

    def get_fields(self, request):
        """called by parse_query_params to get the list of fields"""
        fields = []
        i = 0
        while True:
            col = 'columns[%d][%s]'
            data = get_param(request, col % (i, 'data'))
            if data == "":  # null or empty string on datatables (JS) side
                fields.append({'searchable': False, 'orderable': False})
                i += 1
                continue
            # break out only when there are no more fields to get.
            if data is None:
                break
            name = get_param(request, col % (i, 'name'))
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
                'searchable': get_param(
                    request, col % (i, 'searchable')
                ) == 'true',
                'orderable': get_param(
                    request, col % (i, 'orderable')
                ) == 'true',
                'search_value': get_param(
                    request, '%s[%s]' % (search_col, 'value')
                ),
                'search_regex': get_param(
                    request, '%s[%s]' % (search_col, 'regex')
                ) == 'true',
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
        ret = []
        i = 0
        while True:
            col = 'order[%d][%s]'
            idx = get_param(request, col % (i, 'column'))
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
            dir_ = get_param(request, col % (i, 'dir'), 'asc')
            ret.append((field, dir_))
            i += 1
        return ret

    def get_queryset_count_before(self, request, queryset, view):
        """called by filter_queryset to count the unfiltered queryset

        Provide an overrideable method to return a custom count.
        This can be useful for very large tables, as calls to model.count()
        can be very expensive.

        """
        return queryset.count()

    def get_queryset_count_after(self, request, queryset, view):
        """called by filter_queryset to count the filtered queryset

        See
        :meth:`~rest_framework_datatables.filters.DatatablesBaseFilterBackend.get_queryset_count_before`.

        """
        return count_rows(queryset)

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

    def append_additional_ordering(self, ordering, view):
        if len(ordering):
            if hasattr(view, 'datatables_additional_order_by'):
                additional = view.datatables_additional_order_by
                # Django will actually only take the first occurrence if the
                # same column is added multiple times in an order_by, but it
                # feels cleaner to double check for duplicate anyway.
                if not any((o[1:] if o[0] == '-' else o) == additional
                           for o in ordering):
                    ordering.append(additional)


def uses_default_counts(backend_class):
    """helper function that tells if a backend counts with the default hooks

    The default hooks count the queryset, so their result can be reused
    wherever the same queryset would be counted again. An overridden
    hook may return a cached or estimated number instead, which only
    its own caller should use.

    """
    return all(
        getattr(backend_class, name)
        is getattr(DatatablesBaseFilterBackend, name)
        for name in ('get_queryset_count_before', 'get_queryset_count_after')
    )


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

        total_count = self.get_queryset_count_before(
            request, view.get_queryset(), view
        )
        self.set_count_before(view, total_count)

        if (len(getattr(view, 'filter_backends', [])) > 1
                or not uses_default_counts(type(self))):
            # case of a view with more than 1 filter backend, or of a
            # count before filtering that may not be the queryset's count
            filtered_count_before = self.get_queryset_count_after(
                request, queryset, view
            )
        else:
            filtered_count_before = total_count

        datatables_query = self.parse_datatables_query(request, view)

        q = self.get_q(datatables_query)
        if q:
            queryset = queryset.filter(q).distinct()
            filtered_count = self.get_queryset_count_after(
                request, queryset, view
            )
        else:
            filtered_count = filtered_count_before
        self.set_count_after(view, filtered_count)

        ordering = self.get_ordering(request, view, datatables_query['fields'])
        if ordering:
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_q(self, datatables_query):
        q = Q()
        initial_q = Q()
        for f in datatables_query['fields']:
            if not f['searchable']:
                continue
            q |= f_search_q(f,
                            datatables_query['search_value'],
                            datatables_query['search_regex'])
            initial_q &= f_search_q(f,
                                    f.get('search_value'),
                                    f.get('search_regex', False))
        q &= initial_q
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
        self.append_additional_ordering(ordering, view)
        return ordering
