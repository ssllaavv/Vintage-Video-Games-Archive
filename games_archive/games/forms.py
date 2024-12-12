from django import forms

from .models import Game, Screenshot, GameReview
from ..custom_widgets import ConsoleSelectMultiple, CustomImageUploadWidget


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'release_year', 'developer', 'genre', 'description', 'cover_image', 'to_consoles']
        widgets = {
            'release_year': forms.TextInput,
            'to_consoles': ConsoleSelectMultiple,
            'cover_image': CustomImageUploadWidget,
        }


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshot
        fields = ['picture']
        widgets = {
            'picture':  CustomImageUploadWidget,
        }


class GameReviewForm(forms.ModelForm):
    class Meta:
        model = GameReview
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your review here...',
            }),
        }


class GameSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search games...'
        })
    )


