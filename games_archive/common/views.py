from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import GameRating, ConsoleRating, GameComment, ConsoleComment
from games_archive.games.models import Game
from games_archive.consoles.models import Console
from .forms import GameRatingForm, ConsoleRatingForm, GameCommentForm, ConsoleCommentForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_games'] = Game.objects.order_by('-id')[:5]
        context['latest_consoles'] = Console.objects.order_by('-id')[:5]
        return context


class AddGameRatingView(LoginRequiredMixin, CreateView):
    model = GameRating
    form_class = GameRatingForm
    template_name = 'game_rating_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
        return super().form_valid(form)


class AddConsoleRatingView(LoginRequiredMixin, CreateView):
    model = ConsoleRating
    form_class = ConsoleRatingForm
    template_name = 'console_rating_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_console = Console.objects.get(pk=self.kwargs['console_id'])
        return super().form_valid(form)


class AddGameCommentView(LoginRequiredMixin, CreateView):
    model = GameComment
    form_class = GameCommentForm
    template_name = 'game_comment_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
        return super().form_valid(form)


class AddConsoleCommentView(LoginRequiredMixin, CreateView):
    model = ConsoleComment
    form_class = ConsoleCommentForm
    template_name = 'console_comment_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_console = Console.objects.get(pk=self.kwargs['console_id'])
        return super().form_valid(form)


class SearchView(ListView):
    template_name = 'search_results.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            game_results = Game.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
            console_results = Console.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
            return list(game_results) + list(console_results)
        return []

