from django import forms

from .models import Console
from ..custom_widgets import CustomImageUploadWidget


class ConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['name', 'manufacturer', 'release_year', 'description', 'cover_image', 'logo']
        widgets = {
            'release_year': forms.TextInput,
            'cover_image': CustomImageUploadWidget,
            'logo': CustomImageUploadWidget,
        }


class ConsoleSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search consoles...'
        })
    )
