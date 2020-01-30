from django.db.models import Q

from .filterset import replace_last_lookup


class GlobalFilter(object):
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
        assert hasattr(self, 'global_search_value'), (
            'Must be used with e.g. DatatablesFilterSet to ensure '
            'global_search_value is set')
        if self.global_search_value:
            ret = Q(**{self.global_lookup: self.global_search_value})
        return ret

    @property
    def global_lookup(self):
        return ('{}__{}'
                .format(self.field_name,
                        replace_last_lookup(self.lookup_expr,
                                            self.global_lookup_type)))

    @property
    def global_lookup_type(self):
        assert hasattr(self, 'global_search_regex'), (
            'Must be used with e.g. DatatablesFilterSet to ensure '
            'global_search_regex is set')
        if self.global_search_regex:
            return 'iregex'
        return 'icontains'
