from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('games/<int:game_pk>/rate/', views.add_game_rating, name='rate_game'),
    path('games/<int:game_pk>/user-rating/', views.get_user_rating, name='get_user_rating'),
    path('consoles/<int:console_pk>/rate/', views.AddConsoleRatingView.as_view(), name='rate_console'),
    path('games/<int:game_pk>/comment/', views.AddGameCommentView.as_view(), name='comment_game'),
    path('console/<int:console_pk>/comment/', views.AddConsoleCommentView.as_view(), name='comment_console'),
    path('searchs/', views.SearchView.as_view(), name='search'),
]
