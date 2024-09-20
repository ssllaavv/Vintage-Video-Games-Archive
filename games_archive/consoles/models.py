from django.db import models


class Console(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='console_covers/')

    def __str__(self):
        return self.name








