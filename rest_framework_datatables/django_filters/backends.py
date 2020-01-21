from rest_framework_datatables import filters
from django_filters.rest_framework.backends import DjangoFilterBackend


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
