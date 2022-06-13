import uuid

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    username = models.CharField(
            'username',
            max_length=20,
            unique=True,
            primary_key=True,
            help_text='Required. 20 characters or fewer. Letters and digits only.',
            validators=[validators.RegexValidator(r'^[a-zA-Z0-9]*$',
                                                  'Enter a valid username. This value may contain only letters and digits ')],
            error_messages={'unique': "A user with that username already exists."},
    )

    email = models.EmailField('email address',
                              unique=True,
                              error_messages={'unique': "A user with that email already exists."},
                              blank=False)

    person_group_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
