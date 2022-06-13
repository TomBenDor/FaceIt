from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, TemplateView

from .forms import PhotoCreateForm, AlbumForm, PhotoAlbumsForm
from .models import Album, Photo, Permission, Person
from .utils import get_access_to_album


class PhotoView(UserPassesTestMixin, DetailView):
    model = Photo
    template_name = 'albums/photo.html'

    def test_func(self):
        return self.request.user == self.get_object().owner

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseNotFound()

        return super(PhotoView, self).handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super(PhotoView, self).get_context_data(**kwargs)
        context['form'] = PhotoAlbumsForm()
        return context


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    template_name = 'albums/album_create.html'
    form_class = AlbumForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(AlbumCreateView, self).form_valid(form)


class AlbumEditView(UserPassesTestMixin, UpdateView):
    model = Album
    template_name = 'albums/album_edit.html'
    form_class = AlbumForm

    def test_func(self):
        return get_access_to_album(self.request.user, self.get_object()) == Permission.AccessLevel.MANAGE

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseNotFound()

        return super(AlbumEditView, self).handle_no_permission()

    def get_initial(self):
        initial = super(AlbumEditView, self).get_initial()
        permissions = Permission.objects.filter(album=self.get_object())
        d = dict(Permission.AccessLevel.choices)
        initial['permissions'] = '\n'.join(f"{p.user.username}:{d[p.access]}" for p in permissions)
        return initial


def home_view(request):
    return redirect('my-albums')


class GalleryView(View):
    title = ''
    description = ''
    photos = None
    read_only = True
    handle_remove_photo = None
    handle_add_photo = None
    edit_link = None
    album_id = None

    def get(self, request):
        return render(request, 'albums/album.html',
                      {'title': self.title, 'description': self.description, 'photos': self.photos,
                       'read_only': self.read_only, 'edit_link': self.edit_link, 'album_id': self.album_id})

    def post(self, request):
        if self.read_only:
            return HttpResponseNotFound()

        if 'id' in request.POST:
            photo = get_object_or_404(Photo, pk=request.POST['id'])
            self.handle_remove_photo(photo)
        else:
            form = PhotoCreateForm(request.POST, request.FILES, user=request.user)

            if form.is_valid():
                photo = form.save()
                self.handle_add_photo(photo)

        return redirect(self.request.path)


def album_view(request, pk):
    album = get_object_or_404(Album, pk=pk)

    def remove_photo(photo):
        album.photos.remove(photo)

    def add_photo(photo):
        album.photos.add(photo)

    access = get_access_to_album(request.user, album)

    if access is None:
        return redirect('/account/login/?next=' + reverse('album', kwargs={'pk': pk}))

    if access == Permission.AccessLevel.MANAGE:
        return GalleryView.as_view(title=album.title,
                                   description=album.description,
                                   read_only=album.read_only,
                                   photos=album.photos.all(),
                                   handle_remove_photo=remove_photo,
                                   handle_add_photo=add_photo,
                                   edit_link=reverse('album-edit', kwargs={'pk': album.pk}),
                                   album_id=pk)(request)

    if access == Permission.AccessLevel.READ:
        return GalleryView.as_view(title=album.title,
                                   description=album.description,
                                   read_only=True,
                                   photos=album.photos.all(),
                                   album_id=pk)(request)

    if access == Permission.AccessLevel.WRITE:
        return GalleryView.as_view(title=album.title,
                                   description=album.description,
                                   read_only=album.read_only,
                                   photos=album.photos.all(),
                                   handle_remove_photo=remove_photo,
                                   handle_add_photo=add_photo,
                                   album_id=pk)(request)

    messages.warning(request, "You don't have permission to view this album.")
    return redirect('home')


class AlbumsView(LoginRequiredMixin, TemplateView):
    template_name = 'albums/albums.html'

    def get_context_data(self, **kwargs):
        owned = [(album, 3) for album in Album.objects.filter(owner=self.request.user)]
        editor = [(album, 2) for album in
                  Album.objects.filter(permission__access=2, permission__user=self.request.user)]
        viewer = [(album, 1) for album in
                  Album.objects.filter(permission__access=1, permission__user=self.request.user)]
        manage = [(album, 3) for album in
                  Album.objects.filter(permission__access=3, permission__user=self.request.user)]

        return {
            'albums_dict': [
                ('Created by you', owned),
                ('You can view', viewer),
                ('You are an editor', editor),
                ('You can manage', manage)
            ]
        }


class PersonsView(LoginRequiredMixin, TemplateView):
    template_name = "albums/persons.html"

    def get_context_data(self, **kwargs):
        unnamed = Person.objects.filter(owner=self.request.user, name__exact="Unknown", nameable=True)
        named = Person.objects.filter(owner=self.request.user, nameable=True).difference(unnamed)

        return {
            'persons_dict': [
                ('Named persons', named),
                ('Unnamed persons', unnamed)
            ]
        }


@login_required()
def my_photos_view(request):
    def remove_photo(photo):
        photo.delete()

    return GalleryView.as_view(title=f"Your Photos",
                               description="All your photos will appear here.",
                               read_only=False,
                               photos=Photo.objects.filter(owner=request.user),
                               handle_remove_photo=remove_photo,
                               handle_add_photo=lambda photo: None)(request)


def face_view(request, pk):
    person = get_object_or_404(Person, pk=pk)

    return GalleryView.as_view(title=f"{person.name}'s Photos",
                               description=f"All photos of {person.name} will appear here.",
                               read_only=True,
                               edit_link=reverse('face-edit', kwargs={'pk': person.pk}),
                               photos=person.photos.all())(request)


class FaceEditView(UserPassesTestMixin, UpdateView):
    model = Person
    fields = ['name']
    template_name = 'albums/person_edit.html'

    def test_func(self):
        return self.request.user == self.get_object().owner

    def get_success_url(self):
        return reverse('face', kwargs={'pk': self.object.pk})
