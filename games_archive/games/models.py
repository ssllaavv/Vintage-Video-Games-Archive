from django.core import validators
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import functions
from django.template.defaultfilters import slugify
from django.templatetags.static import static

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console, Supplier
from games_archive.custom_validators import validate_name_is_longer_than_2_characters, validate_release_year, \
    validate_file_size
from games_archive.custom_widgets import get_star_rating_html, get_default_superuser


class Game(models.Model):

    DEFAULT_IMAGE = static('/images/added/no-image2.jpg')

    title = models.CharField(
        validators=[
            validate_name_is_longer_than_2_characters,
        ],
        max_length=100,
    )
    release_year = models.IntegerField(
        validators=[
            validate_release_year,
        ],
        blank=True,
        null=True,
    )
    developer = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(
        validators=[
            validators.MaxLengthValidator(1000)
        ],
        blank=True,
        null=True,
    )
    cover_image = models.ImageField(
        validators=[
            validate_file_size,
        ],
        upload_to='game_covers/',
        blank=True,
        null=True,
    )
    to_consoles = models.ManyToManyField(Console, blank=True,)
    to_user = models.ForeignKey(
        GamesArchiveUser,
        on_delete=models.SET_DEFAULT,
        default=get_default_superuser
    )

    @property
    def rating(self):
        if self.gamerating_set.count() > 0:
            return sum(rating.rating for rating in self.gamerating_set.all()) / self.gamerating_set.count()
        else:
            return 0

    @property
    def stars_rating_html(self):
        return get_star_rating_html(self.rating)

    @property
    def developer_logo(self):
        supplier = Supplier.objects.filter(name__icontains=self.developer).first()
        if supplier and supplier.logo and supplier.logo.name and default_storage.exists(supplier.logo.name):
            return supplier.logo
        return None

    @property
    def default_image(self):
        if self.cover_image.name and default_storage.exists(self.cover_image.name):
            return self.cover_image.url
        else:
            return self.DEFAULT_IMAGE

    def __str__(self):
        return f'{self.title} - pk {self.pk} - form user {self.to_user.pk}'

    class Meta:
        ordering = ['-pk']
        constraints = [
            models.UniqueConstraint(
                functions.Lower('title'),
                name='unique_game_title_ci',
                violation_error_message=f"Game with this title already exists!"
            )
        ]


class Screenshot(models.Model):
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    picture = models.ImageField(
        validators=[
            validate_file_size,
        ],
        upload_to='game_screenshots/',
    )
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f"{self.to_game.title}-{self.from_user.username}-{self.pk}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug


class GameReview(models.Model):
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(
        validators=[
            validators.MaxLengthValidator(2500)
        ],
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.get_user_name()}'s review of {self.to_game.title}"
