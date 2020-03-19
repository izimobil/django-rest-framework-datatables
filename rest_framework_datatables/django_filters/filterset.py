from django_filters.rest_framework.filterset import FilterSet

from .filters import SwitchRegexFilter


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
        for filter_ in self.filters.values():
            self._propagate_to_filter(filter_)

    def _propagate_to_filter(self, filter_):
        self._set_global_info(filter_)
        if filter_.field_name in self.datatables_query['field_queries']:
            query = self.datatables_query['field_queries'][filter_.field_name]
            filter_.datatables_query = query
            self._set_regex_info(filter_)

    def _set_global_info(self, filter_):
        filter_._global_search_value = self.datatables_query['search_value']
        filter_._global_search_regex = self.datatables_query['search_regex']

    def _set_regex_info(self, filter_):
        if filter_.datatables_query.get('search_regex'):
            filter_.lookup_expr = SwitchRegexFilter.replace_last_lookup(
                filter_.lookup_expr,
                'iregex')
