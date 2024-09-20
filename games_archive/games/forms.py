from django import forms
from .models import Game, Screenshots, GameReview


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'release_year', 'developer', 'genre', 'description', 'cover_image', 'to_consoles']


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshots
        fields = ['picture']


class GameReviewForm(forms.ModelForm):
    class Meta:
        model = GameReview
        fields = ['content']

