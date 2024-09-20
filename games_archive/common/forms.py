from django import forms
from .models import GameRating, ConsoleRating, GameComment, ConsoleComment


class GameRatingForm(forms.ModelForm):
    class Meta:
        model = GameRating
        fields = ['rating']


class ConsoleRatingForm(forms.ModelForm):
    class Meta:
        model = ConsoleRating
        fields = ['rating']


class GameCommentForm(forms.ModelForm):
    class Meta:
        model = GameComment
        fields = ['comment']


class ConsoleCommentForm(forms.ModelForm):
    class Meta:
        model = ConsoleComment
        fields = ['comment']

