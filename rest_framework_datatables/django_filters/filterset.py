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
        self._propagate_datatables_query()

    def _propagate_datatables_query(self):
        """propagate parsed datatables query information to filters"""
        for name, filter_ in self.filters.items():
            self._propagate_to_filter(name, filter_)

    def _propagate_to_filter(self, filter_name, filter_):
        self._set_global_info(filter_)
        if filter_name in self.datatables_query['field_queries']:
            query = self.datatables_query['field_queries'][filter_name]
            filter_.datatables_query = query

    def _set_global_info(self, filter_):
        filter_._global_search_value = self.datatables_query['search_value']
        filter_._global_search_regex = self.datatables_query['search_regex']
