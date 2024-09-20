from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('game/<int:game_id>/rate/', views.AddGameRatingView.as_view(), name='rate_game'),
    path('console/<int:console_id>/rate/', views.AddConsoleRatingView.as_view(), name='rate_console'),
    path('game/<int:game_id>/comment/', views.AddGameCommentView.as_view(), name='comment_game'),
    path('console/<int:console_id>/comment/', views.AddConsoleCommentView.as_view(), name='comment_console'),
    path('search/', views.SearchView.as_view(), name='search'),
]