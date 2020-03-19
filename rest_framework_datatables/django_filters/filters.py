from django.db.models import Q


class SwitchRegexFilter(object):
    @classmethod
    def replace_last_lookup(cls, lookup_expr, replacement):
        lookups = lookup_expr.split('__')
        lookups[-1] = replacement
        return '__'.join(lookups)


class GlobalFilter(SwitchRegexFilter):
    """Simple global filter mixin that duplicates the behaviour of the
    global filtering without using django-filter.

    *Must* be used with DjangoFilterBackend which combines the global
    and colum searches in the correct way and with
    DatatablesFilterSet, which ensures that the correct attributes are
    set to make this work.

    For more fine-grained control over global filter behaviour, you
    should implement the global_q method yourself.

    Examples
    --------

    >>> class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    ...     pass
    ...

    >>> class AlbumGlobalFilter(AlbumFilter):
    ...     name = GlobalCharFilter(lookup_expr='icontains')
    ...     genres = GlobalCharFilter(lookup_expr='name__icontains')
    ...     artist = GlobalCharFilter(lookup_expr='name__icontains')
    ...     year = GlobalCharFilter()
    ...     class Meta:
    ...         model = Album
    ...         fields = '__all__'
    ...

    see tests/test_django_filter_backend.py

    """

    def global_q(self):
        """Return a Q-Object for the local search for this column"""
        ret = Q()
        if self.global_search_value:
            ret = Q(**{self.global_lookup: self.global_search_value})
        return ret

    @property
    def global_lookup(self):
        return ('{}__{}'
                .format(self.field_name,
                        self.replace_last_lookup(self.lookup_expr,
                                                 self.global_lookup_expr)))

    @property
    def global_lookup_expr(self):
        if self.global_search_regex:
            return 'iregex'
        return 'icontains'

    @property
    def global_search_regex(self):
        assert hasattr(self, '_global_search_regex'), (
            'Must be used with e.g. DatatablesFilterSet to ensure '
            '_global_search_regex is set')
        return self._global_search_regex

    @property
    def global_search_value(self):
        assert hasattr(self, '_global_search_value'), (
            'Must be used with e.g. DatatablesFilterSet to ensure '
            '_global_search_value is set')
        return self._global_search_value
