from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from .models import Game, Screenshot, GameReview
from .forms import GameForm, ScreenshotForm, GameReviewForm
from ..common.forms import GameRatingForm


class GameListView(ListView):
    model = Game
    template_name = 'game_list.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game_rating_form'] = GameRatingForm()  # Add the rating form to the context
        return context


class GameDetailView(DetailView):
    model = Game
    template_name = 'game_detail.html'
    context_object_name = 'game'


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'game_form.html'
    success_url = reverse_lazy('game_list')


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'game_form.html'

    def test_func(self):
        game = self.get_object()
        result = self.request.user == game.to_user
        if self.request.user.is_staff:
            result = True
        return result

    def get_success_url(self):
        game = self.get_object()
        return reverse_lazy('game_detail', kwargs={'pk': game.pk})


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = 'game_confirm_delete.html'
    success_url = reverse_lazy('game_list')

    def test_func(self):
        game = self.get_object()
        result = self.request.user == game.to_user
        if self.request.user.is_staff:
            result = True
        return result


class AddScreenshotView(LoginRequiredMixin, CreateView):
    model = Screenshot
    form_class = ScreenshotForm
    template_name = 'screenshot_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
        return super().form_valid(form)


class AddReviewView(LoginRequiredMixin, CreateView):
    model = GameReview
    form_class = GameReviewForm
    template_name = 'review_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
        return super().form_valid(form)
