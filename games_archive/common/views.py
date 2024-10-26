from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import GameRating, ConsoleRating, GameComment, ConsoleComment
from games_archive.games.models import Game
from games_archive.consoles.models import Console
from .forms import GameRatingForm, ConsoleRatingForm, GameCommentForm, ConsoleCommentForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import FormView
from .models import GameRating, Game
from .forms import GameRatingForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_games'] = Game.objects.order_by('-id')[:5]
        context['latest_consoles'] = Console.objects.order_by('-id')[:5]
        return context


# @login_required
# def add_game_rating(request, game_pk):
#     game = Game.objects.get(pk=game_pk)
#     existing_rating = GameRating.objects.filter(from_user=request.user, to_game=game).first()
#     game_rating_form = GameRatingForm(request.POST, instance=existing_rating)
#     context = {
#         'game_rating_form': game_rating_form,
#     }
#     if request.method == 'POST':
#         # Handle both update and new rating logic
#         game_rating_form = GameRatingForm(request.POST, instance=existing_rating)
#         if game_rating_form.is_valid():
#             rating = game_rating_form.save(commit=False)
#             rating.to_game = game
#             rating.from_user = request.user
#             rating.save()
#             return redirect(request.META['HTTP_REFERER'] + f'#game-{game_pk}', context=context)
#     else:
#         # Initialize the form with the existing rating or create a new one
#         game_rating_form = GameRatingForm(instance=existing_rating)
#
#     # Return the form to be rendered within the current template
#     return redirect(request.META['HTTP_REFERER'] + f'#game-{game_pk}', context=context)
#


@require_http_methods(["POST"])
@login_required
def add_game_rating(request, game_pk):
    try:
        game = get_object_or_404(Game, pk=game_pk)
        data = json.loads(request.body)
        rating_value = int(data.get('rating'))

        if not 1 <= rating_value <= 5:
            return JsonResponse({'error': 'Invalid rating value'}, status=400)

        rating, created = GameRating.objects.update_or_create(
            from_user=request.user,
            to_game=game,
            defaults={'rating': rating_value}
        )

        message = 'Rating created successfully' if created else 'Rating updated successfully'
        return JsonResponse({
            'message': message,
            'rating': rating_value,
            'average_rating': game.rating,
            'stars_html': game.stars_rating_html
        })

    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_user_rating(request, game_pk):
    try:
        game = get_object_or_404(Game, pk=game_pk)
        rating = GameRating.objects.filter(
            from_user=request.user,
            to_game=game
        ).first()

        return JsonResponse({
            'rating': rating.rating if rating else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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

