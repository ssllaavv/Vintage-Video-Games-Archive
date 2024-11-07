from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='game_list'),
    path('add/', views.GameCreateView.as_view(), name='game_create'),
    path('<int:pk>/', include([
        path('',  views.GameDetailView.as_view(), name='game_detail'),
        path('edit/', views.GameUpdateView.as_view(), name='game_update'),
        path('delete/', views.GameDeleteView.as_view(), name='game_delete'),
        path('add_screenshot/', views.add_game_screenshot, name='add_screenshot'),
        path('add_review/', views.AddOrUpdateReviewView.as_view(), name='add_review'),
        path('delete_review/', views.DeleteReviewView.as_view(), name='delete_review'),
    ])),
    path('screenshot/<int:pk>/delete/', views.DeleteScreenshotView.as_view(), name='delete_screenshot'),
]

