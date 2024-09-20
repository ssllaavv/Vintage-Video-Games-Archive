from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('games_archive.common.urls')),
    path('games/', include('games_archive.games.urls')),
    path('consoles/', include('games_archive.consoles.urls')),
    path('accounts/', include('games_archive.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    