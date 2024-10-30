from django.contrib import admin

from games_archive.common.models import GameRating, ConsoleRating, GameComment, ConsoleComment


# Register your models here.

@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsoleRating)
class ConsoleRatingAdmin(admin.ModelAdmin):
    pass


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsoleComment)
class ConsoleCommentAdmin(admin.ModelAdmin):
    pass

