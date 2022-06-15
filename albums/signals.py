from background_task import background
from django.db.models.signals import post_save, pre_delete
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

        if not person.nameable and len(person_ids) == 1:
            person.nameable = True
            person.thumbnail = photo

        person.save()


# Identify faces in photo
@receiver(post_save, sender=Photo)
def process_image_on_upload(sender, instance, created, **kwargs):
    if created:
        identify_faces(str(instance.pk))


@receiver(pre_delete, sender=Photo)
def on_photo_delete(sender, instance, **kwargs):
    if Person.objects.filter(thumbnail=instance).exists():
        person = Person.objects.get(thumbnail=instance)

        if person.photos.count() == 1:
            person.nameable = False

        for photo in person.photos.all():
            if photo.pk != instance.pk:
                if Person.objects.filter(photos__in=[photo.pk]) == 1:
                    person.thumbnail = photo
                    break
        else:
            person.nameable = False

        person.save()
