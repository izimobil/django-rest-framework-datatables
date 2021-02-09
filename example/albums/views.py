from django.shortcuts import render
from django_filters import widgets, fields, filters, NumberFilter, CharFilter

from rest_framework import viewsets, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_datatables import pagination as dt_pagination
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend

from .models import Album, Artist, Genre
from .serializers import AlbumSerializer, ArtistSerializer


def index(request):
    return render(request, 'albums/albums.html')


def get_album_options():
    return "options", {
        "artist": [{'label': obj.name, 'value': obj.pk} for obj in Artist.objects.all()],
        "genre": [{'label': obj.name, 'value': obj.pk} for obj in Genre.objects.all()]
    }


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all().order_by('rank')
    serializer_class = AlbumSerializer

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )


class ArtistViewSet(viewsets.ViewSet):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )


class AlbumPostListView(generics.ListAPIView):
    queryset = Album.objects.all().order_by('rank')
    serializer_class = AlbumSerializer
    pagination_class = dt_pagination.DatatablesLimitOffsetPagination

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class YADCFMultipleChoiceWidget(widgets.QueryArrayWidget):
    def value_from_datadict(self, data, files, name):
        if name not in data:
            return None
        vals = data[name].split("|")
        new_data = data.copy()
        new_data[name] = vals
        return super().value_from_datadict(new_data, files, name)


class YADCFModelMultipleChoiceField(fields.ModelMultipleChoiceField):
    widget = YADCFMultipleChoiceWidget


class YADCFModelMultipleChoiceFilter(filters.ModelMultipleChoiceFilter):
    field_class = YADCFModelMultipleChoiceField


class AlbumFilter(DatatablesFilterSet):

    # the name of this attribute must match the declared 'name' attribute in
    # the DataTables column
    artist_name = YADCFModelMultipleChoiceFilter(
        field_name="artist", queryset=Artist.objects.all()
    )

    # additional attributes need to be declared so that sorting works
    # the field names must match those declared in the DataTables columns.
    rank = NumberFilter()
    name = CharFilter()

    class Meta:
        model = Album
        fields = ("artist",)


class AlbumFilterListView(generics.ListAPIView):
    # select_related() and prefetch_related provide more efficient DB queries
    queryset = Album.objects.all().select_related("artist").prefetch_related("genres").order_by('rank')
    serializer_class = AlbumSerializer
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = AlbumFilter


class AlbumFilterArtistOptionsListView(APIView):
    """
    Return the list of options to appear in the Albums 'artist' column filter.
    """
    allowed_methods = ("GET",)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        artists = list(
            Artist.objects.filter()
            .values_list("id", "name")
            .order_by("name")
            .distinct()
        )
        options = list()
        for id_, name in artists:
            options.append({"value": str(id_), "label": name})
        return Response(data={"options": options}, status=status.HTTP_200_OK)