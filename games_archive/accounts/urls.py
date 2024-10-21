import django.contrib.auth.forms
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', include([
        path('', views.UserDetailView.as_view(), name='profile details'),
        path('edit/', views.UserEditView.as_view(), name='profile_edit'),
        path('edit/', views.UserEditView.as_view(), name='profile edit'),
        path('delete/', views.UserDeleteView.as_view(), name='profile delete'),
        # TODO: password change & password changed
        # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
        # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    ])),
]


