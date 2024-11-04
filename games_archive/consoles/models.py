from django.db import models
from games_archive.accounts.models import GamesArchiveUser
from games_archive.custom_widgets.custom_widgets import get_star_rating_html


class Console(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='console_covers/', null=True, blank=True)
    logo = models.ImageField(upload_to='console_covers/', null=True, blank=True)
    to_user = models.ForeignKey(GamesArchiveUser, on_delete=models.DO_NOTHING)

    @property
    def rating(self):
        if self.consolerating_set.count() > 0:
            return sum(rating.rating for rating in self.consolerating_set.all()) / self.consolerating_set.count()
        else:
            return 0

    @property
    def stars_rating_html(self):
        return get_star_rating_html(self.rating)

    @property
    def manufacturer_logo(self):
        supplier = Supplier.objects.filter(name__icontains=self.manufacturer).first()
        return supplier.logo if supplier else None

    @property
    def default_image(self):
        if self.cover_image:
            return self.cover_image
        elif self.logo:
            return self.logo
        elif self.manufacturer_logo:
            return self.manufacturer_logo
        return None

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='suppliers_logos/')

    def __str__(self):
        return self.name
