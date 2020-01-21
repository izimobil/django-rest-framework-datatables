from rest_framework_datatables import filters
from django_filters.rest_framework.backends import DjangoFilterBackend


class DatatablesFilterBackend(filters.DatatablesFilterBackend,
                              DjangoFilterBackend):
    pass
