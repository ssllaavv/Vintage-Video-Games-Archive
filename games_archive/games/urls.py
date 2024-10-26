from django.urls import path
from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='game_list'),
    path('<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('add/', views.GameCreateView.as_view(), name='game_create'),
    path('<int:pk>/edit/', views.GameUpdateView.as_view(), name='game_update'),
    path('<int:pk>/delete/', views.GameDeleteView.as_view(), name='game_delete'),
    path('<int:game_id>/add_screenshot/', views.AddScreenshotView.as_view(), name='add_screenshot'),
    path('<int:game_id>/add_review/', views.AddOrUpdateReviewView.as_view(), name='add_review'),
]