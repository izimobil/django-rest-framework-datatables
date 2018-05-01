from rest_framework import serializers

from .models import Album, Artist


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.ReadOnlyField(source='artist.name')
    genres = serializers.SerializerMethodField()

    def get_genres(self, album):
        return ', '.join([str(genre) for genre in album.genres.all()])

    # If you want, you can add special fields understood by Datatables,
    # the fields starting with DT_Row will always be serialized.
    # See: https://datatables.net/manual/server-side#Returned-data
    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    def get_DT_RowId(self, album):
        return 'row_%d' % album.pk

    def get_DT_RowAttr(self, album):
        return {'data-pk': album.pk}

    class Meta:
        model = Album
        fields = (
            'DT_RowId', 'DT_RowAttr', 'rank', 'name',
            'year', 'artist_name', 'genres',
        )


class ArtistSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    # Specifying fields in DT_ALWAYS_SERIALIZE will also
    # force them to always be serialized.
    DT_ALWAYS_SERIALIZE = ('id',)

    class Meta:
        model = Artist
        fields = (
            'id', 'name',
        )
