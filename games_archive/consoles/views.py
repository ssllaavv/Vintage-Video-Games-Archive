from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Console
from .forms import ConsoleForm
from ..common.forms import ConsoleCommentForm


class ConsoleListView(ListView):
    model = Console
    template_name = 'console_list.html'
    context_object_name = 'consoles'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['console_comment_form'] = ConsoleCommentForm()
        return context


class ConsoleDetailView(DetailView):
    model = Console
    template_name = 'console_detail.html'
    context_object_name = 'console'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.consolecomment_set.all()
        context['console_comment_form'] = ConsoleCommentForm()
        popular_games = sorted(
            self.object.game_set.all(),
            key=lambda game: game.rating,
            reverse=True
        )
        context['popular_games'] = popular_games
        return context


class ConsoleCreateView(LoginRequiredMixin, CreateView):
    model = Console
    form_class = ConsoleForm
    template_name = 'console_form.html'

    def form_valid(self, form):
        # Set the to_user field to the currently logged-in user
        form.instance.to_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the detail page of the created game
        return reverse_lazy('console_detail', kwargs={'pk': self.object.pk})


class ConsoleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Console
    form_class = ConsoleForm
    template_name = 'console_form.html'


    def get_success_url(self):
        # Redirect to the detail page of the created game
        return reverse_lazy('console_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return self.request.user == self.object.to_user


class ConsoleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Console
    template_name = 'console_confirm_delete.html'
    success_url = reverse_lazy('console_list')

    def test_func(self):
        return self.request.user.is_staff

