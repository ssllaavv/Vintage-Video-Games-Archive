from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Console
from .forms import ConsoleForm


class ConsoleListView(ListView):
    model = Console
    template_name = 'console_list.html'
    context_object_name = 'consoles'
    paginate_by = 10


class ConsoleDetailView(DetailView):
    model = Console
    template_name = 'console_detail.html'
    context_object_name = 'console'


class ConsoleCreateView(LoginRequiredMixin, CreateView):
    model = Console
    form_class = ConsoleForm
    template_name = 'console_form.html'
    success_url = reverse_lazy('console_list')


class ConsoleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Console
    form_class = ConsoleForm
    template_name = 'console_form.html'
    success_url = reverse_lazy('console_list')

    def test_func(self):
        return self.request.user.is_staff


class ConsoleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Console
    template_name = 'console_confirm_delete.html'
    success_url = reverse_lazy('console_list')

    def test_func(self):
        return self.request.user.is_staff

