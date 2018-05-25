from collections import OrderedDict

from django.utils import six
from django.core.paginator import InvalidPage

from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination, LimitOffsetPagination
)


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
    def paginate_queryset(self, queryset, request, view=None):
        if request.accepted_renderer.format != 'datatables':
            self.is_datatable_request = False
            return super(
                DatatablesPageNumberPagination, self
            ).paginate_queryset(queryset, request, view)
        if request.query_params.get('length') is None:
            return None
        self.count, self.total_count = self.get_count_and_total_count(
            queryset, view
        )
        self.is_datatable_request = True
        self.page_size_query_param = 'length'
        page_size = self.get_page_size(request)
        if not page_size:  # pragma: no cover
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        start = int(request.query_params.get('start', 0))
        page_number = int(start / page_size) + 1

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)
        self.request = request
        return list(self.page)


class DatatablesLimitOffsetPagination(DatatablesMixin, LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if request.accepted_renderer.format == 'datatables':
            self.is_datatable_request = True
            if request.query_params.get('length') is None:
                return None
            self.limit_query_param = 'length'
            self.offset_query_param = 'start'
            self.count, self.total_count = self.get_count_and_total_count(
                queryset, view
            )
        else:
            self.is_datatable_request = False
        return super(
            DatatablesLimitOffsetPagination, self
        ).paginate_queryset(queryset, request, view)
