from django.db import models
from django.contrib.auth.models import AbstractUser


class GamesArchiveUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile-pictures/', blank=True, null=True)
    gender = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.username}: {self.get_full_name()} '



