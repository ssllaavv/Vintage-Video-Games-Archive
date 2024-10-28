from django import forms
from .models import Console
from ..custom_widgets.custom_widgets import CustomImageUploadWidget


class ConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['name', 'manufacturer', 'release_year', 'description', 'cover_image']
        widgets = {
            'release_year': forms.TextInput,
            'cover_image': CustomImageUploadWidget,
        }