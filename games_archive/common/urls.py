from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('games/<int:game_pk>/rate/', views.add_game_rating, name='rate_game'),
    path('games/<int:game_pk>/user-rating/', views.get_user_rating_to_game, name='get_user_rating_to_game'),
    path('consoles/<int:console_pk>/rate/', views.add_console_rating, name='rate_console'),
    path('consoles/<int:console_pk>/user-rating/', views.get_user_rating_to_console, name='get_user_rating_to_console'),
    path('games/<int:game_pk>/comment/', views.add_game_comment, name='comment_game'),
    path('console/<int:console_pk>/comment/', views.add_console_comment, name='comment_console'),
    path('searchs/', views.SearchView.as_view(), name='search'),
]
