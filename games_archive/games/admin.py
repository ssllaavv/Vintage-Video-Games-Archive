from django.contrib import admin

from games_archive.games.models import Game, GameReview, Screenshot


# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'developer', 'genre', 'to_user', 'release_year']
    list_filter = ['developer']
    search_fields = ['pk', 'title', 'developer', 'to_user__pk', 'to_user__username', 'release_year']
    search_help_text = 'Search by: pk, title, developer, user pk, username, year'


@admin.register(Screenshot)
class ScreenshotsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'to_game', 'from_user', 'picture']
    search_fields = ['pk', 'to_game__pk', 'to_game__title', 'from_user__pk', 'from_user__username']
    search_help_text = 'Search by pk, user pk, username, game pk, game title'


@admin.register(GameReview)
class GameReviewAdmin(admin.ModelAdmin):
    list_display = ['pk', 'to_game', 'from_user', 'created_on']
    search_fields = ['pk', 'to_game__pk', 'to_game__title', 'from_user__pk', 'from_user__username']
    search_help_text = 'Search ny pk, game pk, game  title, user pk, username'



