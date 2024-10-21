from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators
from .custom_validators import validate_name


class GamesArchiveUser(AbstractUser):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Do not show', 'Do not show')
    )

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
        null=True,
    )
    gender = models.CharField(
        max_length=15,
        choices=GENDER_CHOICES,
        default='Do not show',
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

    def get_user_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name or self.last_name:
            return self.first_name or self.last_name
        else:
            return self.username

