from django import forms
from .models import ConsoleRating, GameComment, ConsoleComment


# class GameRatingForm(forms.ModelForm):
#     class Meta:
#         model = GameRating
#         fields = ['rating']
#         # widgets = {
#         #     'rating': forms.RadioSelect
#         # }


# class ConsoleRatingForm(forms.ModelForm):
#     class Meta:
#         model = ConsoleRating
#         fields = ['rating']


class GameCommentForm(forms.ModelForm):
    class Meta:
        model = GameComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'Add comment...',
                    'class': 'comment-textarea',
                    'maxlength': 500,
                }
            ),
        }


class ConsoleCommentForm(forms.ModelForm):
    class Meta:
        model = ConsoleComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'Add comment...',
                    'class': 'comment-textarea',
                    'maxlength': 500,
                }
            ),
        }

