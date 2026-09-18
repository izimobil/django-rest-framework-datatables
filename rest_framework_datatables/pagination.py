from collections import OrderedDict

from django.core.paginator import InvalidPage

from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination, LimitOffsetPagination
)

try:
    from django.utils import six
    text_type = six.text_type  # pragma: no cover
except ImportError:
    text_type = str

from .filters import DatatablesBaseFilterBackend, uses_default_counts
from .utils import get_param


class DatatablesMixin(object):
    def get_paginated_response(self, data):
        if not self.is_datatable_request:
            return super(DatatablesMixin, self).get_paginated_response(data)

        return Response(OrderedDict([
            ('recordsTotal', self.total_count),
            ('recordsFiltered', self.count),
            ('data', data)
        ]))

    def get_count_and_total_count(self, queryset, view):
        if hasattr(view, '_datatables_filtered_count'):
            count = view._datatables_filtered_count
            del view._datatables_filtered_count
        else:  # pragma: no cover
            count = queryset.count()
        if hasattr(view, '_datatables_total_count'):
            total_count = view._datatables_total_count
            del view._datatables_total_count
        else:  # pragma: no cover
            total_count = count
        return count, total_count


class DatatablesPageNumberPagination(DatatablesMixin, PageNumberPagination):
    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                size = int(get_param(request, self.page_size_query_param))
                if size <= 0:
                    raise ValueError()
                if self.max_page_size is not None:
                    return min(size, self.max_page_size)
                return size
            except (ValueError, TypeError):
                pass
        return self.page_size

    def get_page(self, request, page_size):
        try:
            start = int(get_param(request, self.page_query_param, 0))
            return int(start / page_size) + 1
        except ValueError:
            return None

    def paginate_queryset(self, queryset, request, view=None):
        if request.accepted_renderer.format != 'datatables':
            self.is_datatable_request = False
            return super(
                DatatablesPageNumberPagination, self
            ).paginate_queryset(queryset, request, view)

        self.page_query_param = 'start'
        self.page_size_query_param = 'length'
        length = get_param(request, self.page_size_query_param)

        if length == '-1':
            return None
        self.count, self.total_count = self.get_count_and_total_count(
            queryset, view
        )
        self.is_datatable_request = True
        page_size = self.get_page_size(request)
        if not page_size:  # pragma: no cover
            return None

        class CachedCountPaginator(self.django_paginator_class):
            def __init__(self, value, *args, **kwargs):
                self.value = value
                super(CachedCountPaginator, self).__init__(*args, **kwargs)

            @property
            def count(self):
                return self.value

        paginator = CachedCountPaginator(self.count, queryset, page_size)
        page_number = self.get_page(request, page_size)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=text_type(exc)
            )
            raise NotFound(msg)
        self.request = request
        return list(self.page)


class DatatablesLimitOffsetPagination(DatatablesMixin, LimitOffsetPagination):
    use_filter_backend_count = False

    def get_limit(self, request):
        try:
            limit_value = int(get_param(request, self.limit_query_param))
            if limit_value <= 0:
                raise ValueError

            if self.max_limit is not None:
                return min(limit_value, self.max_limit)
            return limit_value
        except (ValueError, TypeError):
            return self.default_limit

    def get_offset(self, request):
        try:
            offset_value = int(get_param(request, self.offset_query_param))
            if offset_value < 0:
                raise ValueError

            return offset_value
        except (ValueError, TypeError):
            return 0

    def get_count(self, queryset):
        """the filter backend already counted the filtered queryset

        Without this, LimitOffsetPagination.paginate_queryset would
        overwrite the count taken from the view with an identical query
        of its own.

        """
        if self.is_datatable_request and self.reuse_count:
            return self.count
        return super(
            DatatablesLimitOffsetPagination, self
        ).get_count(queryset)

    def paginate_queryset(self, queryset, request, view=None):
        if request.accepted_renderer.format == 'datatables':
            self.is_datatable_request = True
            self.limit_query_param = 'length'
            self.offset_query_param = 'start'
            if get_param(request, self.limit_query_param) == '-1':
                return None
            self.count, self.total_count = self.get_count_and_total_count(
                queryset, view
            )
            self.reuse_count = self.trusts_filter_backend_count(view)
        else:
            self.is_datatable_request = False
        return super(
            DatatablesLimitOffsetPagination, self
        ).paginate_queryset(queryset, request, view)

    def trusts_filter_backend_count(self, view):
        """called by paginate_queryset to know if the view's count is exact

        A count from the default hooks is exact. An overridden hook may
        return a cached or estimated number, and DRF returns an empty
        page for any offset past the count, so an undercount would hide
        rows. The paginator counts again then, unless
        use_filter_backend_count opts in to trusting the override.

        """
        if self.use_filter_backend_count:
            return True
        return all(
            uses_default_counts(backend)
            for backend in getattr(view, 'filter_backends', [])
            if issubclass(backend, DatatablesBaseFilterBackend)
        )


class DatatablesOnlyPageNumberPagination(DatatablesPageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if request.accepted_renderer.format != 'datatables':
            return None
        else:
            return super().paginate_queryset(queryset, request, view)
