from django.db.models.signals import post_save
from django.dispatch import receiver

from faceapi import FaceAPI
from .models import User


@receiver(post_save, sender=User)
def create_person_group(sender, instance, created, **kwargs):
    if created:
        FaceAPI().create_person_group(instance.person_group_id, f"{instance.username}'s Person Group")
