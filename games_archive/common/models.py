from django.core.validators import MaxLengthValidator
from django.db import models

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game


# auxiliary function creating rating options
def create_rating_options(max_rating):
    options = []
    for i in range(1, max_rating + 1):
        options.append((i, i))
    return options


class RatingMixin(models.Model):
    MAX_RATING_VALUE = 5
    RATING_OPTIONS = create_rating_options(MAX_RATING_VALUE)

    rating = models.IntegerField(
        choices=RATING_OPTIONS,
        blank=True,
        null=True
    )

    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class CommentMixin(models.Model):
    comment = models.TextField(
        validators=[
            MaxLengthValidator(700),
        ],
    )
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created_on']


class GameRating(RatingMixin):
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rating} stars from user {self.from_user.pk} to game {self.to_game.pk} (rating pk {self.pk})"

    class Meta:
        unique_together = ('from_user', 'to_game')


class ConsoleRating(RatingMixin):
    to_console = models.ForeignKey(Console, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rating} stars from user {self.from_user.pk} to console {self.to_console.pk} (rating pk {self.pk})"

    class Meta:
        unique_together = ('from_user', 'to_console')


class GameComment(CommentMixin):
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment {self.pk} form user {self.from_user.pk} to game {self.to_game.pk} {self.created_on}'


class ConsoleComment(CommentMixin):
    to_console = models.ForeignKey(Console, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment {self.pk} form user {self.from_user.pk} to console {self.to_console.pk} {self.created_on}'
