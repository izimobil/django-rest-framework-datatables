from rest_framework_datatables import filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from django_filters import utils


class DatatablesFilterBackend(filters.DatatablesBaseFilterBackend,
                              DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.accepted_renderer.format != 'datatables':
            return queryset

        filtered_count_before = self.count_before(queryset, view)

        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            self.set_count_after(view, filtered_count_before)
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        # TODO combine the global search with OR for every field
        queryset = filterset.qs

        self.set_count_after(view, queryset.count())
        return queryset

    def get_filterset_kwargs(self, request, queryset, view):
        # parse query params
        query = self.parse_query_params(request, view)
        return {
            'data': query['form_fields'],
            'queryset': queryset,
            'request': request,
            # 'datatables_query': query
        }

    def parse_query_params(self, request, view):
        query = super(DatatablesFilterBackend,
                      self).parse_query_params(request, view)
        form_fields = {}
        for f in query['fields']:
            form_fields[f['data']] = f['search_value']
        query['form_fields'] = form_fields
        return query
