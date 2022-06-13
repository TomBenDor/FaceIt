from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

from .models import Photo, Album
from .utils import get_access_to_album
from .views import PhotoView, AlbumCreateView, home_view, AlbumsView, my_photos_view, album_view, AlbumEditView, \
    face_view, FaceEditView, PersonsView


def get_album_photo_image(request, album_pk, photo_pk):
    photo = get_object_or_404(Photo, pk=photo_pk)
    if request.user == photo.owner:
        return redirect(photo.image.url)

    album = get_object_or_404(Album, pk=album_pk)

    if album.photos.filter(pk=photo.pk).exists() and get_access_to_album(request.user, album):
        return redirect(photo.image.url)

    return HttpResponseNotFound()


def get_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)

    if request.user == photo.owner:
        return redirect(photo.image.url)

    return HttpResponseNotFound()


urlpatterns = [
    path('', home_view, name='home'),
    path('my-photos/', my_photos_view, name='my-photos'),
    path('my-albums/', AlbumsView.as_view(), name='my-albums'),
    path('album/<str:pk>', album_view, name='album'),
    path('album/<str:pk>/edit', AlbumEditView.as_view(), name='album-edit'),
    path('photo/<str:pk>', PhotoView.as_view(), name='photo'),
    path('photo/<str:pk>/image', get_photo, name='photo-image'),
    path('album/<str:album_pk>/<str:photo_pk>', get_album_photo_image, name='album-photo-image'),
    path('create-album/', AlbumCreateView.as_view(), name='create-album'),
    path('persons/', PersonsView.as_view(), name='persons'),
    path('face/<str:pk>', face_view, name='face'),
    path('face/<str:pk>/edit', FaceEditView.as_view(), name='face-edit'),
]
