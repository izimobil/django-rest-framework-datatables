"""
Generate random album data for load testing.
Add 'django_extensions' to INSTALLED_APPS, then run with:

./manage.py runscript create_albums
"""

import random

from django.utils import timezone
from django.utils.crypto import get_random_string

from albums import models

# Modify this value to increase the number of albums created per artist
ALBUMS_PER_ARTIST = 1


def run(*args):
    start = timezone.now()
    albums = []
    count = 0
    for artist in models.Artist.objects.all():
        for i in range(ALBUMS_PER_ARTIST):
            count += 1
            album = models.Album(
                name=get_random_string(length=16, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ '),
                artist=artist,
                rank=random.randint(1, 99),
                year=random.randint(1950, 2023),
            )
            albums.append(album)
            if count % 10000 == 0:
                models.Album.objects.bulk_create(albums)
                albums.clear()
                print(f"created {count} albums")
    if len(albums) > 0:
        models.Album.objects.bulk_create(albums)

    print(f"created {count} Albums in {timezone.now() - start}")


