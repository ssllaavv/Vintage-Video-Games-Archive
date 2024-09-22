from django.contrib.auth.models import AbstractUser
from django.db import models
from games_archive.mixins import ResizeImageMixin
from django.core import validators
from .custom_validators import validate_name


class GamesArchiveUser(AbstractUser,  ResizeImageMixin):
    email = models.EmailField(
        validators=[
            validators.EmailValidator
        ],
        unique=True
    )
    first_name = models.CharField(
        validators=[
           validate_name,
        ],
        max_length=50,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        validators=[
            validate_name,
        ],
        max_length=50,
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(
        upload_to='profile-pictures/',
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    age = models.IntegerField(
        validators=[
            validators.MinValueValidator(0)
        ],
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # Convert first_name and last_name to proper case
        if self.first_name:
            self.first_name = self.first_name.capitalize()

        if self.last_name:
            self.last_name = self.last_name.capitalize()

        super(GamesArchiveUser, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.username}: {self.email} '



