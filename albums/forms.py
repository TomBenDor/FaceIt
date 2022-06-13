import re

from django import forms
from django.utils.safestring import mark_safe

from albums.models import Photo, Album, Permission
from users.models import User


class PhotoCreateForm(forms.ModelForm):
    image = forms.ImageField(label='Upload a photo')

    class Meta:
        model = Photo
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user') if 'user' in kwargs else None
        super(PhotoCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        photo = super(PhotoCreateForm, self).save(commit=False)
        photo.owner = self.user
        if commit:
            photo.save()
        return photo


class PhotoAlbumsForm(forms.Form):
    albums = forms.ModelMultipleChoiceField(queryset=Album.objects.all(),
                                            widget=forms.CheckboxSelectMultiple,
                                            required=False,
                                            label='')


def validate_permissions(value):
    value = value.strip()
    perms = re.split("\r?\n", value)
    for i, perm in enumerate(perms, start=1):
        if not re.fullmatch("[a-zA-Z0-9]+ *: *(View|Edit|Manage)", perm):
            raise forms.ValidationError(f"Line {i} doesn't match the format '<username>:<permission>'")

    for perm in perms:
        username, perm = re.split(" *: *", perm)
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"User '{username}' does not exist")


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'allow_anonymous_view']

    PERMS_HELP_TEXT = "<p>Should be in the format:<br><br>username1: View<br>username2: Edit<br>username3: Manage</p>"

    permissions = forms.CharField(widget=forms.Textarea(attrs={'name': 'body', 'rows': '3', 'cols': '5'}),
                                  help_text=mark_safe(PERMS_HELP_TEXT),
                                  required=False, validators=[validate_permissions])

    def save(self, commit=True):
        album = super(AlbumForm, self).save(commit)

        Permission.objects.filter(album=album).delete()
        if self.cleaned_data['permissions']:
            for perm in re.split(r"\r?\n", self.cleaned_data['permissions']):
                username, perm = re.split(" *: *", perm)
                user = User.objects.get(username=username)
                Permission.objects.filter(album=album, user=user).delete()
                Permission.objects.create(album=album, user=user, access={'View': 1, 'Edit': 2, 'Manage': 3}[perm])

        return album
