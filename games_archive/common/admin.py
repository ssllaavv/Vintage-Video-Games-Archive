from django.contrib import admin

from games_archive.common.models import GameRating, ConsoleRating, GameComment, ConsoleComment


# Register your models here.
@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_game', 'rating']
    list_filter = ['rating']
    search_fields = ['from_user__pk', 'to_game__pk', 'from_user__username', 'to_game__title']
    search_help_text = 'Search by: user pk, game pk, username, game title'
    ordering = ['to_game__pk']


@admin.register(ConsoleRating)
class ConsoleRatingAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_console', 'rating']
    list_filter = ['rating']
    search_fields = ['from_user__pk', 'to_console__pk', 'from_user__username', 'to_game__title']
    search_help_text = 'Search by: user pk, console pk, username, game title'
    ordering = ['to_console__pk']


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ['to_game', 'from_user', 'created_on']
    search_fields = ['to_game__pk', 'to_game__title', 'from_user__pk', 'from_user__username']
    search_help_text = 'Search by: game pk, game title, user pk, username'


@admin.register(ConsoleComment)
class ConsoleCommentAdmin(admin.ModelAdmin):
    list_display = ['to_console', 'from_user', 'created_on']
    search_fields = ['to_console__pk', 'to_console__name', 'from_user__pk', 'from_user__username']
    search_help_text = 'Search by: console pk, console name, user pk, username'

