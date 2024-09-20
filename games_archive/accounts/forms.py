from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import GamesArchiveUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = GamesArchiveUser
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = GamesArchiveUser
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'gender', 'age']