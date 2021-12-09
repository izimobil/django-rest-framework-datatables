from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from albums import views


router = routers.DefaultRouter()
router.register(r'albums', views.AlbumViewSet)
router.register(r'artists', views.ArtistViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path(
        'api/post-list/albums/',
        views.AlbumPostListView.as_view(),
        name='albums_post_list'
    ),
    path(
        'api/filter/albums/artist/options/',
        views.AlbumFilterArtistOptionsListView.as_view(),
        name='albums_filter_artist_options_list'
    ),
    path(
        'api/filter/albums/',
        views.AlbumFilterListView.as_view(),
        name='albums_filter_list'
    ),
    path('', views.index, name='albums')
]
