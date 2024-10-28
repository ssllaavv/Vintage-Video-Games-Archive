import re

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import GameRating, ConsoleRating, GameComment, ConsoleComment
from games_archive.games.models import Game
from games_archive.consoles.models import Console
from .forms import GameCommentForm, ConsoleCommentForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import FormView
from .models import GameRating, Game


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_games'] = Game.objects.order_by('-id')[:5]
        context['latest_consoles'] = Console.objects.order_by('-id')[:5]
        return context



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
def get_user_rating_to_game(request, game_pk):
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

#
# class AddConsoleRatingView(LoginRequiredMixin, CreateView):
#     model = ConsoleRating
#     # form_class = ConsoleRatingForm
#     # template_name = 'console_rating_form.html'
#
#     def form_valid(self, form):
#         form.instance.from_user = self.request.user
#         form.instance.to_console = Console.objects.get(pk=self.kwargs['console_id'])
#         return super().form_valid(form)
#


@require_http_methods(["POST"])
@login_required
def add_console_rating(request, console_pk):
    try:
        console = get_object_or_404(Console, pk=console_pk)
        data = json.loads(request.body)
        rating_value = int(data.get('rating'))

        if not 1 <= rating_value <= 5:
            return JsonResponse({'error': 'Invalid rating value'}, status=400)

        rating, created = ConsoleRating.objects.update_or_create(
            from_user=request.user,
            to_console=console,
            defaults={'rating': rating_value}
        )

        message = 'Rating created successfully' if created else 'Rating updated successfully'
        return JsonResponse({
            'message': message,
            'rating': rating_value,
            'average_rating': console.rating,
            'stars_html': console.stars_rating_html
        })

    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_user_rating_to_console(request, console_pk):
    try:
        console = get_object_or_404(Console, pk=console_pk)
        rating = ConsoleRating.objects.filter(
            from_user=request.user,
            to_console=console
        ).first()

        return JsonResponse({
            'rating': rating.rating if rating else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def add_game_comment(request, game_pk):
    if request.method == 'POST':
        game = Game.objects.get(pk=game_pk)
        form = GameCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.to_game = game
            comment.from_user = request.user
            comment.save()

        referrer = request.META.get('HTTP_REFERER')
        pattern = r".*games/\d+/.*"
        match = re.search(pattern, referrer)

        if match:
            return redirect(request.META['HTTP_REFERER'] + f'#game-comments-{game_pk}')

    return redirect(request.META['HTTP_REFERER'] + f'#game-{game_pk}')


@login_required
def add_console_comment(request, console_pk):
    if request.method == 'POST':
        console = Console.objects.get(pk=console_pk)
        form = ConsoleCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.to_console = console
            comment.from_user = request.user
            comment.save()

        referrer = request.META.get('HTTP_REFERER')
        pattern = r".*consoles/\d+/.*"
        match = re.search(pattern, referrer)

        if match:
            return redirect(request.META['HTTP_REFERER'] + f'#console-comments-{console_pk}')
        else:
            return redirect(request.META['HTTP_REFERER'] + f'#console-{ console.pk }')


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

