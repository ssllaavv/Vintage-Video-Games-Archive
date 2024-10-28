from django.db import models

from games_archive.accounts.models import GamesArchiveUser
from games_archive.custom_widgets.custom_widgets import get_star_rating_html


class Console(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='console_covers/')
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

    def __str__(self):
        return self.name








