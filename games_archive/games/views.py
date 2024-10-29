from django.db.models import Q
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from .models import Game, Screenshot, GameReview
from .forms import GameForm, ScreenshotForm, GameReviewForm, GameSearchForm
from ..common.forms import GameCommentForm
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..consoles.models import Console


# class GameListView(ListView):
#     model = Game
#     template_name = 'game_list.html'
#     context_object_name = 'games'
#     paginate_by = 10
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['game_comment_form'] = GameCommentForm()
#         return context
#

class GameListView(ListView):
    model = Game
    template_name = 'game_list.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()

        if search_query:
            # First, get console IDs that match the search query
            console_ids = Console.objects.filter(
                name__icontains=search_query
            ).values_list('id', flat=True)

            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(developer__icontains=search_query) |
                Q(to_consoles__in=console_ids) |
                Q(to_user__first_name__icontains=search_query) |
                Q(to_user__last_name__icontains=search_query) |
                Q(to_user__username__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game_comment_form'] = GameCommentForm()
        context['search_form'] = GameSearchForm(self.request.GET)
        context['search_query'] = self.request.GET.get('search', '')
        # Add the fragment identifier to the current URL
        if self.request.GET.get('search'):
            context['current_url'] = f"{self.request.path}?{self.request.GET.urlencode()}#games-list"

        return context




class GameDetailView(DetailView):
    model = Game
    template_name = 'game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['screenshots'] = self.object.screenshot_set.all()
        context['review'] = self.object.reviews.all().first()
        context['comments'] = self.object.gamecomment_set.all()
        context['game_comment_form'] = GameCommentForm()
        return context


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'game_form.html'

    def form_valid(self, form):
        # Set the to_user field to the currently logged-in user
        form.instance.to_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the detail page of the created game
        return reverse_lazy('game_detail', kwargs={'pk': self.object.pk})


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'game_form.html'

    def test_func(self):
        game = self.get_object()
        result = self.request.user == game.to_user
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
        return result


class AddScreenshotView(LoginRequiredMixin, CreateView):
    model = Screenshot
    form_class = ScreenshotForm
    template_name = 'screenshot_form.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
        return super().form_valid(form)


# class AddReviewView(LoginRequiredMixin, CreateView):
#     model = GameReview
#     form_class = GameReviewForm
#     template_name = 'review_form.html'
#
#     def form_valid(self, form):
#         form.instance.from_user = self.request.user
#         form.instance.to_game = Game.objects.get(pk=self.kwargs['game_id'])
#         return super().form_valid(form)

class AddOrUpdateReviewView(LoginRequiredMixin, View):
    template_name = 'review_form.html'
    form_class = GameReviewForm

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['game_id'], to_user=request.user)
        review, created = GameReview.objects.get_or_create(
            from_user=request.user,
            to_game=game,
            defaults={'content': ''}  # Provide a default if a new review is created
        )
        form = self.form_class(instance=review)
        return render(request, self.template_name, {'form': form, 'game': game})

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['game_id'], to_user=request.user)
        review, created = GameReview.objects.get_or_create(
            from_user=request.user,
            to_game=game
        )
        form = self.form_class(request.POST, instance=review)

        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('game_detail', kwargs={'pk': game.id}))  # or any other page

        return render(request, self.template_name, {'form': form, 'game': game})
