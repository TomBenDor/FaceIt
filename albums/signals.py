from PIL import Image
from background_task import background
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from albums.models import Photo, Person
from faceapi import FaceAPI


@background()
def identify_faces(photo_pk):
    photo = Photo.objects.get(pk=photo_pk)

    person_ids = list(FaceAPI().identify_faces(photo.owner.person_group_id, photo.image.url))

    for id in person_ids:
        person, _ = Person.objects.get_or_create(pk=id, defaults={'name': 'Unknown'},
                                                 owner=photo.owner)
        person.photos.add(photo)
        if len(person_ids) == 1:
            person.nameable = True
        person.save()

    try:
        img = Image.open("." + photo.image.url)
    except ValueError:
        return
    if img.height > settings.MAX_IMAGE_SIZE or img.width > settings.MAX_IMAGE_SIZE:
        new_img = (settings.MAX_IMAGE_SIZE, settings.MAX_IMAGE_SIZE)
        img.thumbnail(new_img)
        img.save("." + photo.image.url)


# Idenify faces in photo
@receiver(post_save, sender=Photo)
def process_image_on_upload(sender, instance, created, **kwargs):
    if created:
        identify_faces.now(str(instance.pk))  # TODO: use background task
