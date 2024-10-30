from django.contrib import admin

from games_archive.consoles.models import Console, Supplier


# Register your models here.
@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    pass


