from django.db import models
from django.core import validators

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game


# Create your models he
def create_rating_options(max_rating):
    options = []
    for i in range(1, max_rating + 1):
        options.append((i, i))
    return options


class GameRating(models.Model):

    MAX_RATING_VALUE = 5
    RATING_OPTIONS = create_rating_options(MAX_RATING_VALUE)

    rating = models.IntegerField(
        choices=RATING_OPTIONS,
        blank=True,
        null=True
    )

    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.DO_NOTHING)
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('from_user', 'to_game')


class ConsoleRating(models.Model):

    MAX_RATING_VALUE = 5

    rating = models.IntegerField(validators=[
        validators.MinValueValidator(0),
        validators.MaxValueValidator(MAX_RATING_VALUE),
    ])
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.DO_NOTHING)
    to_console = models.ForeignKey(Console, on_delete=models.CASCADE)


class GameComment(models.Model):
    comment = models.TextField()
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)


class ConsoleComment(models.Model):
    comment = models.TextField()
    to_console = models.ForeignKey(Console, on_delete=models.CASCADE)
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
