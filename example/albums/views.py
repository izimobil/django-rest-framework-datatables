from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.renderers import DatatablesRenderer
from rest_framework_datatables.viewsets import DatatablesEditorModelViewSet
from .models import Album, Artist, Genre
from .serializers import AlbumSerializer, ArtistSerializer


def index(request):
    return render(request, 'albums/albums.html')


def get_album_options():
    return "options", {
        "artist.id": [{'label': obj.name, 'value': obj.pk} for obj in Artist.objects.all()],
        "genre": [{'label': obj.name, 'value': obj.pk} for obj in Genre.objects.all()]
    }


class AlbumViewSet(DatatablesEditorModelViewSet):
    queryset = Album.objects.all().order_by('rank')
    serializer_class = AlbumSerializer

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )


class ArtistViewSet(viewsets.ViewSet):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer

    filter_backends = (DatatablesFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (DatatablesRenderer,)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )
