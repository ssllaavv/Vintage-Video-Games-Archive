from django import forms

from games_archive.custom_widgets.custom_widgets import ConsoleSelectMultiple, CustomImageUploadWidget
from .models import Game, Screenshot, GameReview


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


class GameReviewForm(forms.ModelForm):
    class Meta:
        model = GameReview
        fields = ['content']

