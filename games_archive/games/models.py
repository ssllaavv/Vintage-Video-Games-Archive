from django.db import models
from django.template.defaultfilters import slugify

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console


# Auxiliary function to generate stars icons for rating
def get_star_rating_html(rating):
    full_stars = int(rating)  # Number of solid stars
    half_star = 1 if rating - full_stars >= 0.5 else 0  # Determine if there's a half star
    empty_stars = 5 - full_stars - half_star  # The rest will be empty stars

    # Generate the HTML for the star rating
    stars_html = ''
    stars_html += '<i class="fas fa-star"></i>' * full_stars
    stars_html += '<i class="fas fa-star-half-alt"></i>' * half_star
    stars_html += '<i class="far fa-star"></i>' * empty_stars

    return stars_html


class Game(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField(blank=True, null=True)
    developer = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='game_covers/', blank=True, null=True)
    to_consoles = models.ManyToManyField(Console)
    to_user = models.ForeignKey(GamesArchiveUser, on_delete=models.DO_NOTHING)

    @property
    def rating(self):
        if self.gamerating_set.count() > 0:
            return sum(rating.rating for rating in self.gamerating_set.all()) / self.gamerating_set.count()
        else:
            return 0

    @property
    def stars_rating_html(self):
        return get_star_rating_html(self.rating)

    def __str__(self):
        return self.title


class Screenshot(models.Model):
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='game_screenshots/')
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f"{self.to_game.title}-{self.from_user.username}-{self.pk}")

    def __str__(self):
        return self.slug


class GameReview(models.Model):
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username}'s review of {self.to_game.title}"
