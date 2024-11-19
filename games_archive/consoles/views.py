from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import Console
from .forms import ConsoleForm, ConsoleSearchForm
from ..common.forms import ConsoleCommentForm


class ConsoleListView(ListView):
    model = Console
    template_name = 'console_list.html'
    context_object_name = 'consoles'
    paginate_by = 10

    def get_queryset(self):
        # Get base queryset
        queryset = super().get_queryset()

        # Store search query as instance variable
        self.search_query = self.request.GET.get('search', '').strip()

        if self.search_query:
            # Apply all filters at once
            queryset = queryset.filter(
                Q(name__icontains=self.search_query) |
                # Q(description__icontains=self.search_query) |
                Q(manufacturer__icontains=self.search_query)
            ).distinct().order_by('-id')  # Add explicit ordering to ensure consistent pagination

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create forms for each game
        for console in context['consoles']:

            if (self.request.session.get('invalid_comment_form') and
                    self.request.session.get('invalid_comment_console_pk') == console.pk):
                # Create form with invalid data
                form = ConsoleCommentForm(self.request.session['invalid_comment_form'])
                # Clear the session data
                del self.request.session['invalid_comment_form']
                del self.request.session['invalid_comment_console_pk']

            elif (self.request.session.get('message') and
                  self.request.session.get('message_console_pk') == console.pk):
                form = ConsoleCommentForm()
                form.message = self.request.session.get('message')
                del self.request.session['message']
                del self.request.session['message_console_pk']
            else:
                # Create empty form
                form = ConsoleCommentForm()

            # Store the form in the game object
            console.comment_form = form

        context['search_form'] = ConsoleSearchForm(self.request.GET)
        context['search_query'] = self.search_query
        return context


class ConsoleDetailView(DetailView):
    model = Console
    template_name = 'console_detail.html'
    context_object_name = 'console'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.consolecomment_set.all()

        # Check if there's an invalid form for this game
        if (self.request.session.get('invalid_comment_form') and
                self.request.session.get('invalid_comment_console_pk') == self.object.pk):
            # Create form with invalid data
            form = ConsoleCommentForm(self.request.session['invalid_comment_form'])
            # Clear the session data
            del self.request.session['invalid_comment_form']
            del self.request.session['invalid_comment_console_pk']
        else:
            form = ConsoleCommentForm()

        context['console_comment_form'] = form

        popular_games = sorted(
            self.object.game_set.all(),
            key=lambda game: game.rating,
            reverse=True
        )
        if len(popular_games) > 6:
            popular_games = popular_games[:6]
        context['popular_games'] = popular_games

        return context


class ConsoleCreateView(LoginRequiredMixin, CreateView):
    model = Console
    form_class = ConsoleForm
    template_name = 'console_form.html'

    def form_valid(self, form):
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
        return reverse_lazy('console_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        console = self.get_object()
        return self.request.user == console.to_user or self.request.user.is_staff


class ConsoleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Console
    template_name = 'console_confirm_delete.html'
    success_url = reverse_lazy('console_list')

    def test_func(self):
        return self.request.user.is_staff

