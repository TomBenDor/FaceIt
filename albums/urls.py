from django.urls import path

from .views import (PhotoView, AlbumCreateView, home_view, AlbumsView, my_photos_view, album_view, AlbumEditView,
                    person_view, FaceEditView, PersonsView)

urlpatterns = [
    path('', home_view, name='home'),
    path('my-photos/', my_photos_view, name='my-photos'),
    path('my-albums/', AlbumsView.as_view(), name='my-albums'),
    path('album/<str:pk>', album_view, name='album'),
    path('album/<str:pk>/edit', AlbumEditView.as_view(), name='album-edit'),
    path('photo/<str:pk>', PhotoView.as_view(), name='photo'),
    path('create-album/', AlbumCreateView.as_view(), name='create-album'),
    path('persons/', PersonsView.as_view(), name='persons'),
    path('person/<str:pk>', person_view, name='person'),
    path('person/<str:pk>/edit', FaceEditView.as_view(), name='face-edit'),
]
