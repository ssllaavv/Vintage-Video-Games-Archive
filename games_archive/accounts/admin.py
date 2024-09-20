from django.contrib import admin

from games_archive.accounts.models import GamesArchiveUser


# Register your models here.
@admin.register(GamesArchiveUser)
class GamesArchiveUserAdmin(admin.ModelAdmin):
    pass
