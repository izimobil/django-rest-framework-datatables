from django.conf import settings
from django.db.models import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from django_filters import utils

from rest_framework_datatables import filters

from .filterset import DatatablesFilterSet


class DatatablesFilterBackend(filters.DatatablesBaseFilterBackend,
                              DjangoFilterBackend):

    filterset_base = DatatablesFilterSet

    def __init__(self):
        super().__init__()
        rest_framework_datatables_settings = getattr(settings, "REST_FRAMEWORK_DATATABLES", dict())
        self.disable_count = rest_framework_datatables_settings.get("DISABLE_COUNT", False)

    def filter_queryset(self, request, queryset, view):
        """Filter DataTables queries with a filterset

        This method needs to combine the necessary steps from both its
        superclasses.

        """
        if not self.check_renderer_format(request):
            return queryset

        if not self.disable_count:
            self.set_count_before(view, view.get_queryset().count())

        # parsed datatables_query will be an attribute of the filterset
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            if not self.disable_count:
                self.set_count_after(view, queryset.count())
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        queryset = filterset.qs
        global_q = self.get_global_q(filterset)
        if global_q:
            queryset = queryset.filter(global_q).distinct()

        if not self.disable_count:
            self.set_count_after(view, queryset.count())

        # TODO Can we use OrderingFilter, maybe in DatatablesFilterSet, by
        # default? See
        # https://django-filter.readthedocs.io/en/master/ref/filters.html#ordering-filter
        ordering = self.get_ordering(request, view, filterset)
        if ordering:
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_filterset_kwargs(self, request, queryset, view):
        query = self.parse_datatables_query(request, view)
        return {
            'data': query['form_fields'],
            'queryset': queryset,
            'request': request,
            'datatables_query': query
        }

    def parse_datatables_query(self, request, view):
        query = super().parse_datatables_query(request, view)
        form_fields = {}
        field_queries = {}
        for f in query['fields']:
            if 'data' not in f:
                continue

            form_fields[f['data']] = f['search_value']
            field_queries[f['data']] = f
        query['form_fields'] = form_fields
        query['field_queries'] = field_queries
        return query

    def get_global_q(self, filterset):
        global_q = Q()
        for filter_name, f in filterset.filters.items():
            if (
                    filter_name in filterset.datatables_query['field_queries']
                    and hasattr(f, 'global_q')):
                global_q |= f.global_q()
        return global_q

    def get_ordering(self, request, view, filterset):
        ret = []
        for field, dir_ in self.get_ordering_fields(
                request, view, filterset.datatables_query['fields']):
            if field['data'] in filterset.filters:
                filter = filterset.filters[field['data']]
                lookup = '__'.join(
                    f'{filter.field_name}__{filter.lookup_expr}'
                    .split('__')
                    [:-1])
                ret.append(('-' if dir_ == 'desc' else '')
                           + lookup)
        self.append_additional_ordering(ret, view)
        return ret
