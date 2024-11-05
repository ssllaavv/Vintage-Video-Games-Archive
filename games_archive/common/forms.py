from django import forms
from .models import GameComment, ConsoleComment


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

