from django_filters.rest_framework.filterset import FilterSet


class DatatablesFilterSet(FilterSet):
    """Basic FilterSet used by default in DatatablesFilterBackend
    Datatables parameters are parsed and only the relevant parts are
    stored and propagated to the filters

    """

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None,
                 datatables_query=None):
        super().__init__(data=data, queryset=queryset,
                         request=request, prefix=prefix)
        self.datatables_query = datatables_query
        self.propagate_datatables_query()

    def propagate_datatables_query(self):
        """propagate parsed datatables query information to filters"""
        for filter_ in self.filters.values():
            filter_.global_search_value = self.datatables_query['search_value']
            if filter_.field_name in self.datatables_query['field_queries']:
                query = self.datatables_query['field_queries'][filter_.field_name]
                filter_.datatables_query = query
                if query.get('search_regex'):
                    lookups = filter_.lookup_expr.split('__')
                    lookups[-1] = 'iregex'
                    filter_.lookup_expr = '__'.join(lookups)
