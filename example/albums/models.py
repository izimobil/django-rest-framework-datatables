from django.db import models


class Genre(models.Model):
    name = models.CharField('Name', max_length=80)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField('Name', max_length=80)

    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'
        ordering = ['name']

    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField('Name', max_length=80)
    rank = models.PositiveIntegerField('Rank')
    year = models.PositiveIntegerField('Year')
    artist = models.ForeignKey(
        Artist,
        models.CASCADE,
        verbose_name='Artist',
        related_name='albums'
    )
    genres = models.ManyToManyField(
        Genre,
        verbose_name='Genres',
        related_name='albums'
    )

    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        ordering = ['name']

    def __str__(self):
        return self.name
