from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import GamesArchiveUser
from .forms import UserRegistrationForm, UserProfileForm


class RegisterView(CreateView):
    model = GamesArchiveUser
    form_class = UserRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')


class ProfileView(LoginRequiredMixin, DetailView):
    model = GamesArchiveUser
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = GamesArchiveUser
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
