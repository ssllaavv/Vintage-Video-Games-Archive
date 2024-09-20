from django.contrib import admin

from games_archive.consoles.models import Console


# Register your models here.
@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    pass


