from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_datatables import pagination as dt_pagination

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
