from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Album, Artist


class ArtistSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    # if we need to edit a field that is a nested serializer,
    # we must override to_internal_value method
    def to_internal_value(self, data):
        return get_object_or_404(Artist, pk=data['id'])

    class Meta:
        model = Artist
        fields = (
            'id', 'name',
        )
        # Specifying fields in datatables_always_serialize
        # will also force them to always be serialized.
        datatables_always_serialize = ('id',)


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.ReadOnlyField(source='artist.name')
    # DRF-Datatables can deal with nested serializers as well.
    artist = ArtistSerializer()
    genres = serializers.SerializerMethodField()
    artist_view = ArtistSerializer(source="artist", read_only=True)

    @staticmethod
    def get_genres(album):
        return ', '.join([str(genre) for genre in album.genres.all()])

    # If you want, you can add special fields understood by Datatables,
    # the fields starting with DT_Row will always be serialized.
    # See: https://datatables.net/manual/server-side#Returned-data
    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    @staticmethod
    def get_DT_RowId(album):
        return album.pk

    @staticmethod
    def get_DT_RowAttr(album):
        return {'data-pk': album.pk}

    class Meta:
        model = Album
        fields = (
            'DT_RowId', 'DT_RowAttr', 'rank', 'name',
            'year', 'artist_name', 'genres', 'artist',
            'artist_view'
        )


