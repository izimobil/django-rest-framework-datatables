import operator
import re
from functools import reduce

from django.core.exceptions import FieldDoesNotExist
from django.db.models import F, ForeignObjectRel, Max, Min, Q
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import OrderBy
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


def is_to_many(model, lookup):
    """helper function that tells if a lookup crosses a to-many relation"""
    for part in lookup.split(LOOKUP_SEP):
        try:
            field = model._meta.get_field(part)
        except FieldDoesNotExist:
            return False
        if field.many_to_many or field.one_to_many:
            return True
        if not field.is_relation:
            return False
        model = field.related_model
    return False


def repeats_objects(query):
    """helper function that tells if a query's joins can repeat an object

    A join across a to-many relation, or a table added with extra(), can
    return an object once for each related row; a join to one related
    object cannot.

    """
    if query.extra_tables:
        return True
    for join in query.alias_map.values():
        field = getattr(join, 'join_field', None)
        if field is not None and reaches_many(field):
            return True
    return False


def reaches_many(field):
    """helper function that tells if a join field reaches many rows

    A reverse relation, including a generic one, says so itself; a
    forward field by its kind.

    """
    if isinstance(field, ForeignObjectRel):
        return field.multiple
    return field.one_to_many or field.many_to_many


def aggregates_safely(query):
    """helper function that tells if a query can be ordered by an aggregate

    An aggregate groups the rows by object, which leaves them as they
    are only when each object is already one row, with DISTINCT or with
    no join that repeats it. Its own aggregates and windows would change
    with the grouping or the added join, and DISTINCT compares its
    extra() columns, so a query with any of those is not grouped.

    """
    if query.group_by is not None or query.extra:
        return False
    if any(getattr(annotation, 'contains_over_clause', False)
           for annotation in query.annotations.values()):
        return False
    return query.distinct or not repeats_objects(query)


def one_value_ordering(queryset, term, name):
    """helper function that orders by one related value instead of each

    Returns the annotations to add and the ordering term to use in place
    of term: the lowest related value, or the highest when term is
    descending. The value comes from the
    rows the queryset keeps, so a search on the relation orders by the
    values it matched. It is an aggregate, added with alias() so a count
    leaves it out.

    """
    descending = term.startswith('-')
    aggregate = (Max if descending else Min)(term.lstrip('-'))
    return {name: aggregate}, OrderBy(F(name), descending=descending)


def unused_name(query, position):
    """helper function that names a sort value no annotation already uses"""
    name = '_datatables_order_%d' % position
    while name in query.annotations:
        name += '_'
    return name


def order_by_one_value(queryset, ordering):
    """helper function that orders a queryset without repeating its rows

    Ordering by a field across a to-many relation joins every related
    row, so each row came back once per related object. Such a field is
    ordered by one related value instead, leaving the rows as the
    queryset returns them, so only when grouping by object keeps them.
    Otherwise, as for a values() queryset, whose rows are not objects,
    the ordering is kept as given.

    """
    query = queryset.query
    if query.values_select or not aggregates_safely(query):
        return queryset.order_by(*ordering)
    annotations = {}
    order_by = []
    for term in ordering:
        if not isinstance(term, str) or not is_to_many(
                queryset.model, term.lstrip('-')):
            order_by.append(term)
            continue
        name = unused_name(queryset.query, len(order_by))
        added, ordered = one_value_ordering(queryset, term, name)
        annotations.update(added)
        order_by.append(ordered)
    if annotations:
        queryset = queryset.alias(**annotations)
    return queryset.order_by(*order_by)


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

        total_count = view.get_queryset().count()
        self.set_count_before(view, total_count)

        if len(getattr(view, 'filter_backends', [])) > 1:
            # case of a view with more than 1 filter backend
            filtered_count_before = queryset.count()
        else:
            filtered_count_before = total_count

        datatables_query = self.parse_datatables_query(request, view)

        q = self.get_q(datatables_query)
        if q:
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = filtered_count_before
        self.set_count_after(view, filtered_count)

        ordering = self.get_ordering(request, view, datatables_query['fields'])
        if ordering:
            queryset = order_by_one_value(queryset, ordering)

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
