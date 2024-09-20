from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConsoleListView.as_view(), name='console_list'),
    path('<int:pk>/', views.ConsoleDetailView.as_view(), name='console_detail'),
    path('add/', views.ConsoleCreateView.as_view(), name='console_create'),
    path('<int:pk>/edit/', views.ConsoleUpdateView.as_view(), name='console_update'),
    path('<int:pk>/delete/', views.ConsoleDeleteView.as_view(), name='console_delete'),
]