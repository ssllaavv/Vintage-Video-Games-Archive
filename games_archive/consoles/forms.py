from django import forms
from .models import Console


class ConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['name', 'manufacturer', 'release_year', 'description', 'cover_image']