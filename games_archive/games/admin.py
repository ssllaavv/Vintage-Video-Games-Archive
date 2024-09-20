from django.contrib import admin

from games_archive.games.models import Game, GameReview, Screenshot


# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass


@admin.register(Screenshot)
class ScreenshotsAdmin(admin.ModelAdmin):
    pass


@admin.register(GameReview)
class GameReviewAdmin(admin.ModelAdmin):
    pass



