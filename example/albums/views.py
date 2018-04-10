from django.shortcuts import render

from rest_framework import viewsets

from .models import Album
from .serializers import AlbumSerializer


def index(request):
    return render(request, 'albums/albums.html')


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all().order_by('rank')
    serializer_class = AlbumSerializer
