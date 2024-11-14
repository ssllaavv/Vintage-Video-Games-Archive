from django.test import TestCase
from django.core.exceptions import ValidationError
from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game
from games_archive.common.forms import GameCommentForm, ConsoleCommentForm
from games_archive.common.models import GameComment, ConsoleComment


class GameCommentFormTests(TestCase):
    def setUp(self):
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            email='test@example.com',
        )
        self.user.set_password('testpass123')
        self.user.full_clean()
        self.user.save()

        self.game = Game.objects.create(
            title='Test Game',
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

    def test_game_comment_form_fields_should_pass(self):
        form = GameCommentForm()
        self.assertEqual(list(form.fields.keys()), ['comment'])

    def test_game_comment_form_valid_data_should_pass(self):
        form_data = {
            'comment': 'This is a valid comment'
        }
        form = GameCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_game_comment_form_empty_data_should_raise(self):
        form_data = {
            'comment': ''
        }
        form = GameCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_game_comment_form_max_length_exceeded_should_raise(self):
        form_data = {
            'comment': 'x' * 701  # One character more than max length
        }
        form = GameCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_game_comment_form_widget_attributes_are_set_correctly(self):
        form = GameCommentForm()
        widget = form.fields['comment'].widget
        self.assertEqual(widget.attrs['placeholder'], 'Add comment...')
        self.assertEqual(widget.attrs['class'], 'comment-textarea')
        self.assertEqual(widget.attrs['maxlength'], 700)

    def test_valid_game_comment_form_save_and_persists(self):
        form_data = {
            'comment': 'Test comment'
        }
        form = GameCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test saving the form with a game and user
        comment = form.save(commit=False)
        comment.to_game = self.game
        comment.from_user = self.user
        comment.save()

        # Verify the comment was saved correctly
        saved_comment = GameComment.objects.first()
        self.assertEqual(saved_comment.comment, 'Test comment')
        self.assertEqual(saved_comment.to_game, self.game)
        self.assertEqual(saved_comment.from_user, self.user)


class ConsoleCommentFormTests(TestCase):
    def setUp(self):
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            email='test@example.com',
        )
        self.user.set_password('testpass123')
        self.user.full_clean()
        self.user.save()

        self.console = Console.objects.create(
            name='Test Console',
            to_user=self.user
        )
        self.console.full_clean()
        self.console.save()

    def test_console_comment_form_fields(self):
        form = ConsoleCommentForm()
        self.assertEqual(list(form.fields.keys()), ['comment'])

    def test_console_comment_form_valid_data_should_pass(self):
        form_data = {
            'comment': 'This is a valid comment'
        }
        form = ConsoleCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_console_comment_form_with_empty_data_should_raise(self):
        form_data = {
            'comment': ''
        }
        form = ConsoleCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_console_comment_form_exceeding__max_length_should_raise(self):
        form_data = {
            'comment': 'x' * 701  # One character more than max length
        }
        form = ConsoleCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_console_comment_widget_attributes_are_set_correctly(self):
        form = ConsoleCommentForm()
        widget = form.fields['comment'].widget
        self.assertEqual(widget.attrs['placeholder'], 'Add comment...')
        self.assertEqual(widget.attrs['class'], 'comment-textarea')
        self.assertEqual(widget.attrs['maxlength'], 700)

    def test_console_comment_form_with_valid_data_should_create_and_persists(self):
        form_data = {
            'comment': 'Test comment'
        }
        form = ConsoleCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test saving the form with a console and user
        comment = form.save(commit=False)
        comment.to_console = self.console
        comment.from_user = self.user
        comment.save()

        # Verify the comment was saved correctly
        saved_comment = ConsoleComment.objects.first()
        self.assertEqual(saved_comment.comment, 'Test comment')
        self.assertEqual(saved_comment.to_console, self.console)
        self.assertEqual(saved_comment.from_user, self.user)


class CommentFormsCommonTests(TestCase):
    """Tests common functionality between both forms"""

    def test_game_comment_and_console_comment_forms_have_same_configuration(self):
        game_form = GameCommentForm()
        console_form = ConsoleCommentForm()

        # Test that both forms have the same widget configuration
        game_widget = game_form.fields['comment'].widget
        console_widget = console_form.fields['comment'].widget

        self.assertEqual(
            game_widget.attrs,
            console_widget.attrs,
            "Both forms should have identical widget attributes"
        )

        # Test that both forms have the same field requirements
        self.assertEqual(
            game_form.fields['comment'].required,
            console_form.fields['comment'].required,
            "Both forms should have the same required field settings"
        )