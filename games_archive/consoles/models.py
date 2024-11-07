from django.core import validators
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import functions
from django.templatetags.static import static

from games_archive.accounts.models import GamesArchiveUser
from games_archive.custom_validators import validate_file_size, validate_name_is_longer_than_2_characters, \
    validate_release_year
from games_archive.custom_widgets import get_star_rating_html


class Console(models.Model):

    DEFAULT_IMAGE = static('/images/added/no-image-default.avif')

    name = models.CharField(
        validators=[
            validate_name_is_longer_than_2_characters,
        ],
        max_length=100,
    )
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    release_year = models.IntegerField(
        validators=[
            validate_release_year,
        ],
        blank=True,
        null=True,
    )
    description = models.TextField(
        validators=[
            validators.MaxLengthValidator(1000)
        ],
        null=True,
        blank=True,
    )
    cover_image = models.ImageField(
        validators=[
            validate_file_size,
        ],
        upload_to='console_covers/',
        null=True,
        blank=True,
    )
    logo = models.ImageField(
        validators=[
            validate_file_size,
        ],
        upload_to='console_covers/',
        null=True,
        blank=True,
    )
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
        if supplier and supplier.logo and supplier.logo.name and default_storage.exists(supplier.logo.name):
            return supplier.logo
        return None

    @property
    def default_image(self):
        if self.cover_image and self.cover_image.name and default_storage.exists(self.cover_image.name):
            return self.cover_image.url
        elif self.logo and self.logo.name and default_storage.exists(self.logo.name):
            return self.logo.url
        else:
            return self.DEFAULT_IMAGE

    def __str__(self):
        return f'Console {self.name} - {self.pk} from user {self.to_user.pk}'

    class Meta:
        ordering = ['-pk']
        constraints = [
            models.UniqueConstraint(
                functions.Lower('name'),
                name='unique_console_name_ci',
                violation_error_message=f"Console with this name already exists!"
            )
        ]


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='suppliers_logos/')

    def __str__(self):
        return f'{self.name} = {self.pk}'
