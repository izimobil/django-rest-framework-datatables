from rest_framework import serializers as drf_serializers
from rest_framework_datatables import serializers

from .models import Album


class AlbumSerializer(serializers.DatatablesModelSerializer):
    artist_name = drf_serializers.ReadOnlyField(source='artist.name')
    genres = drf_serializers.SerializerMethodField()

    def get_genres(self, album):
        return ', '.join([str(genre) for genre in album.genres.all()])

    class Meta:
        model = Album
        fields = (
            'rank', 'name', 'year', 'artist_name', 'genres',
        )
