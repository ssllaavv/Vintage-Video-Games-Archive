
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Game, Screenshot, GameReview
from .forms import GameForm, ScreenshotForm, GameReviewForm, GameSearchForm
from ..common.forms import GameCommentForm
from ..consoles.models import Console


class GameListView(ListView):
    model = Game
    template_name = 'game_list.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_queryset(self):
        # Get base queryset
        queryset = super().get_queryset()

        # Store search query as instance variable
        self.search_query = self.request.GET.get('search', '').strip()

        if self.search_query:
            # Get console IDs that match the search query
            console_ids = Console.objects.filter(
                name__icontains=self.search_query
            ).values_list('id', flat=True)

            # Apply all filters at once
            queryset = queryset.filter(
                Q(title__icontains=self.search_query) |
                Q(description__icontains=self.search_query) |
                Q(developer__icontains=self.search_query) |
                Q(to_consoles__in=console_ids) |
                Q(to_user__first_name__icontains=self.search_query) |
                Q(to_user__last_name__icontains=self.search_query) |
                Q(to_user__username__icontains=self.search_query)
            ).distinct().order_by('-pk')  # Add explicit ordering to ensure consistent pagination

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create forms for each game
        for game in context['games']:
            # Check if this game had an invalid form submission
            if (self.request.session.get('invalid_comment_form') and
                    self.request.session.get('invalid_comment_game_pk') == game.pk):
                # Create form with invalid data
                form = GameCommentForm(self.request.session['invalid_comment_form'])
                # Clear the session data
                del self.request.session['invalid_comment_form']
                del self.request.session['invalid_comment_game_pk']

            elif (self.request.session.get('message') and
                    self.request.session.get('message_game_pk') == game.pk):
                form = GameCommentForm()
                form.message = self.request.session.get('message')
                del self.request.session['message']
                del self.request.session['message_game_pk']
            else:
                # Create empty form
                form = GameCommentForm()

            # Store the form in the game object
            game.comment_form = form

        context['search_form'] = GameSearchForm(self.request.GET)
        context['search_query'] = self.search_query
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

        # Check if there's an invalid form for this game
        if (self.request.session.get('invalid_comment_form') and
                self.request.session.get('invalid_comment_game_pk') == self.object.pk):
            # Create form with invalid data
            form = GameCommentForm(self.request.session['invalid_comment_form'])
            # Clear the session data
            del self.request.session['invalid_comment_form']
            del self.request.session['invalid_comment_game_pk']
        else:
            form = GameCommentForm()

        context['game_comment_form'] = form
        context['add_screenshot_form'] = ScreenshotForm()
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


class AddOrUpdateReviewView(LoginRequiredMixin, View):
    template_name = 'review_form.html'
    form_class = GameReviewForm

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'], to_user=request.user)
        review, created = GameReview.objects.get_or_create(
            from_user=request.user,
            to_game=game,
            defaults={'content': ''}  # Provide a default if a new review is created
        )
        form = self.form_class(instance=review)
        return render(request, self.template_name, {'form': form, 'game': game})

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'], to_user=request.user)
        review, created = GameReview.objects.get_or_create(
            from_user=request.user,
            to_game=game
        )
        form = self.form_class(request.POST, instance=review)

        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('game_detail', kwargs={'pk': game.pk}))
        return render(request, self.template_name, {'form': form, 'game': game})


class DeleteReviewView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = GameReview
    template_name = 'review_confirm_delete.html'

    def get_object(self, queryset=None):
        # Get the review using game_id from URL
        return get_object_or_404(
            GameReview,
            to_game__pk=self.kwargs['pk'],
            from_user=self.request.user
        )

    def test_func(self):
        # Check if the logged-in user is the author of the review
        review = self.get_object()
        return self.request.user == review.from_user

    def get_success_url(self):
        # Redirect to the game detail page after deletion
        return reverse_lazy('game_detail', kwargs={'pk': self.kwargs['pk']})


@login_required
def add_game_screenshot(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.method == 'POST':
        form = ScreenshotForm(request.POST, request.FILES)
        if form.is_valid():
            screenshot = form.save(commit=False)
            screenshot.to_game = game
            screenshot.from_user = request.user
            screenshot.save()
            messages.success(request, 'Screenshot uploaded successfully!')
            return redirect(f'{request.META.get("HTTP_REFERER")}#screenshot-{screenshot.pk}')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    if error == 'This field is required.':
                        messages.error(request, "No file selected")
                    else:
                        messages.error(request, f'{field}: {error}')

    return redirect(f'{request.META.get("HTTP_REFERER")}#add_screenshot')


class DeleteScreenshotView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        screenshot = get_object_or_404(Screenshot, pk=self.kwargs['pk'])
        return self.request.user == screenshot.from_user

    def post(self, request, pk):
        screenshot = get_object_or_404(Screenshot, pk=pk)
        game_id = screenshot.to_game.id

        # Get the previous screenshot's ID if it exists
        previous_screenshot = Screenshot.objects.filter(
            to_game=screenshot.to_game,
            pk__lt=screenshot.pk
        ).order_by('-pk').first()

        # Get the next screenshot'ss ID if previous doesn't exist
        next_screenshot = Screenshot.objects.filter(
            to_game=screenshot.to_game,
            pk__gt=screenshot.pk
        ).order_by('pk').first()

        # Delete the screenshot
        screenshot.delete()

        # Determine redirect target
        if previous_screenshot:
            target = f'#screenshot-{previous_screenshot.pk}'
        elif next_screenshot:
            target = f'#screenshot-{next_screenshot.pk}'
        else:
            target = '#screenshots'

        return JsonResponse({
            'status': 'success',
            'redirect_url': target
        })
