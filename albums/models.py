import os.path
import uuid

from django.db import models
from django.urls import reverse

from users.models import User


def get_upload_path(instance, filename):
    return os.path.join('photos', str(instance.owner.pk), filename)


class Album(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=256)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=30)

    description = models.TextField(max_length=255, blank=True)

    photos = models.ManyToManyField('Photo', blank=True)

    read_only = models.BooleanField(default=False)

    allow_anonymous_view = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('album', kwargs={'pk': self.id})


class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class AccessLevel(models.IntegerChoices):
        READ = 1
        WRITE = 2
        MANAGE = 3

    access = models.IntegerField(choices=AccessLevel.choices)

    album = models.ForeignKey(Album, on_delete=models.CASCADE)


class Photo(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=256)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    image = models.ImageField(upload_to=get_upload_path)

    persons = models.ManyToManyField('Person', blank=True)

    def delete(self, **kwargs):
        self.image.delete()

        super(Photo, self).delete(**kwargs)


class Person(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    person_id = models.CharField(primary_key=True, max_length=128)

    name = models.CharField(max_length=30)

    photos = models.ManyToManyField(Photo, blank=True)

    nameable = models.BooleanField(default=False)

    thumbnail = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True, related_name='thumbnail')
