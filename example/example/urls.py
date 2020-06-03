from django.contrib import admin
from django.conf.urls import url, include

from rest_framework import routers

from albums import views


router = routers.DefaultRouter()
router.register(r'albums', views.AlbumViewSet)
router.register(r'artists', views.ArtistViewSet)


urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^api/', include(router.urls)),
    url('^api/post-list/albums', views.AlbumPostListView.as_view(), name='albums_post_list'),
    url('', views.index, name='albums')
]
