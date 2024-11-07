from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ConsoleListView.as_view(), name='console_list'),
    path('add/', views.ConsoleCreateView.as_view(), name='console_create'),
    path('<int:pk>/', include([
        path('', views.ConsoleDetailView.as_view(), name='console_detail'),
        path('edit/', views.ConsoleUpdateView.as_view(), name='console_update'),
        path('delete/', views.ConsoleDeleteView.as_view(), name='console_delete'),
    ])),
]


