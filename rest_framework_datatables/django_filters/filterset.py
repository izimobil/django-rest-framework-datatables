from django_filters.rest_framework.filterset import FilterSet


class DatatablesFilterSet(FilterSet):
    """Basic FilterSet used by default in DatatablesFilterBackend (see below)
    Datatables parameters are parsed and only the relevant parts are
    stored and propagated to the filters

    """

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None,
                 datatables_query=None):
        super().__init__(data=data, queryset=queryset,
                         request=request, prefix=prefix)
        self.datatables_query = datatables_query
        # Propagate the datatables information to the filters:
        for filter_ in self.filters.values():
            queries = [x for x
                       in datatables_query['fields']
                       if x.get('data') == filter_.field_name]
            if queries:
                filter_.datatables_query = queries[0]
                if filter_.datatables_query.get('search_regex'):
                    lookups = filter_.lookup_expr.split('__')
                    lookups[-1] = 'iregex'
                    filter_.lookup_expr = '__'.join(lookups)
