from django.contrib import admin

from games_archive.consoles.models import Console, Supplier


# Register your models here.
@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'manufacturer', 'release_year', 'to_user']
    list_filter = ['manufacturer', ]
    search_fields = ['pk', 'name', 'manufacturer', 'to_user__pk', 'to_user__username', 'release_year']
    search_help_text = 'Search by: pk, name, manufacturer, user pk, username, year'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'logo']


