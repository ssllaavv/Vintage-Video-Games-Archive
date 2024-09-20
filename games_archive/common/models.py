from django.db import models

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game


# Create your models here


class GameRating(models.Model):
    rating = models.IntegerField(validators=[

    ])
    from_user = models.ForeignKey(GamesArchiveUser, on_delete=models.DO_NOTHING)
    to_game = models.ForeignKey(Game, on_delete=models.CASCADE)


class ConsoleRating(models.Model):
    rating = models.IntegerField(validators=[

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
