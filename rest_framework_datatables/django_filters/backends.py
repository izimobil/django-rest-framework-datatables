from django.db.models import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from django_filters import utils

from rest_framework_datatables import filters

from .filterset import DatatablesFilterSet


class DatatablesFilterBackend(filters.DatatablesBaseFilterBackend,
                              DjangoFilterBackend):

    filterset_base = DatatablesFilterSet

    def filter_queryset(self, request, queryset, view):
        """Filter DataTables queries with a filterset

        This method needs to combine the workflows from both its
        superclasses.
        """
        if request.accepted_renderer.format != 'datatables':
            return queryset

        filtered_count_before = self.count_before(queryset, view)

        # parse query params
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            self.set_count_after(view, filtered_count_before)
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        queryset = filterset.qs
        q = Q()
        for f in filterset.filters.values():
            if hasattr(f, 'global_q'):
                q |= f.global_q()
        if q:
            queryset = queryset.filter(q)

        self.set_count_after(view, queryset.count())
        # TODO Can we use OrderingFilter, maybe in the FilterSet, by
        # default? See
        # https://django-filter.readthedocs.io/en/master/ref/filters.html#ordering-filter
        queryset = queryset.order_by(*self.datatables_query['ordering'])
        return queryset

    def get_filterset_kwargs(self, request, queryset, view):
        query = self.parse_query_params(request, view)
        self.datatables_query = query
        return {
            'data': query['form_fields'],
            'queryset': queryset,
            'request': request,
            'datatables_query': query
        }

    def parse_query_params(self, request, view):
        query = super(DatatablesFilterBackend,
                      self).parse_query_params(request, view)
        form_fields = {}
        for f in query['fields']:
            form_fields[f['data']] = f['search_value']
        query['form_fields'] = form_fields
        return query
