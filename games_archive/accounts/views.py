from django.contrib.auth import views as auth_views, login, get_user_model
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm, UserLoginForm
from django.views import generic as views


from ..common.forms import GameCommentForm
from django.utils.http import url_has_allowed_host_and_scheme


class UserRegisterView(CreateView):
    model = get_user_model()
    form_class = UserRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        result = super().form_valid(form)
        login(self.request, self.object)
        return result

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', None)
        return context

    def get_success_url(self):
        result = self.request.POST.get('next', None)
        if result == 'None' or result.includs('register'):
            return self.success_url
        return result


class UserLoginView(auth_views.LoginView):
    form_class = UserLoginForm
    template_name = 'login.html'

    def get_success_url(self):
        # Retrieve the 'next' parameter from either GET or POST data
        next_url = self.request.POST.get('next') or self.request.GET.get('next')

        # Ensure the 'next' URL is safe
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        return reverse_lazy('home')  # Default redirect if 'next' is missing or invalid


class UserLogoutView(LoginRequiredMixin, auth_views.LogoutView):
    http_method_names = ["post", "options", "get"]
    next_page = 'login'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserProfileForm
    template_name = 'profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile details', kwargs={'pk': self.object.pk})


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'profile-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_count = self.object.gamecomment_set.count() + self.object.consolecomment_set.count()
        rates = self.object.gamerating_set.count() + self.object.consolerating_set.count()

        context.update({
            'comments_count': comments_count,
            'game_comment_form': GameCommentForm(),
            'rates': rates,
        })

        return context


class UserDeleteView(LoginRequiredMixin, views.DeleteView):
    model = get_user_model()
    template_name = 'profile-delete.html'
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return redirect(self.success_url)
