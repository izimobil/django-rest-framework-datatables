from django.db.models import Q


class SwitchRegexFilter(object):

    lookup_regex_replacements = {
      'icontains': 'iregex',
      'contains': 'regex',
      'exact': 'regex',
    }

    def __init__(self, field_name=None, lookup_expr='exact', *, label=None,
                 method=None, distinct=False, exclude=False, **kwargs):
        self._original_lookup_expr = lookup_expr
        super().__init__(
            field_name=field_name, lookup_expr=lookup_expr, label=label,
            method=method, distinct=distinct, exclude=exclude, **kwargs)

    @classmethod
    def replace_last_lookup(cls, lookup_expr, replacement=None):
        lookups = lookup_expr.split('__')
        last_lookup = lookups[-1]
        if replacement is None:
            replacement = cls.lookup_regex_replacements.get(
                last_lookup, last_lookup)
        lookups[-1] = replacement
        return '__'.join(lookups)

    def lookup_expr():
        def fget(self):
            if not self.search_regex:
                return self._original_lookup_expr
            else:
                return self.replace_last_lookup(self._original_lookup_expr)

        def fset(self, value):
            self._original_lookup_expr = value
        return locals()

    lookup_expr = property(**lookup_expr())

    @property
    def search_regex(self):
        # datatables_query is only present, if there's a query for
        # this column, so even if we use the correct backend, it might
        # not be.
        return getattr(self, 'datatables_query', {}).get('search_regex')


class GlobalFilter(SwitchRegexFilter):
    """Simple global filter mixin that duplicates the behaviour of the
    global filtering without using django-filter.

    *Must* be used with DjangoFilterBackend which combines the global
    and column searches in the correct way and with
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
        """Return a Q-Object for the global search for this column"""
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
