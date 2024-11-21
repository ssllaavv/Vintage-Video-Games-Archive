from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game
from games_archive.common.models import GameRating, ConsoleRating, GameComment, ConsoleComment
from games_archive.common.views import (
    add_game_rating, add_console_rating,
    get_user_rating_to_game, get_user_rating_to_console,
    add_game_comment, add_console_comment
)
from games_archive.settings import LOGIN_URL


class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test user
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.set_password('testpass123')
        self.user.full_clean()
        self.user.save()

        # Create test game and console
        self.game = Game.objects.create(
            title='Test Game',
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

        self.console = Console.objects.create(
            name='Test Console',
            to_user=self.user
        )
        self.console.full_clean()
        self.console.save()

    def add_session_to_request(self, request):
        """Helper method to add session to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()


class HomeViewTests(BaseViewTest):
    def test_home_view_uses_correct_template_and_return_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_sets_correct_context(self):
        response = self.client.get(reverse('home'))
        self.assertTrue('latest_games' in response.context)
        self.assertTrue('latest_consoles' in response.context)

    def test_home_view_returns_only_10_consoles_and_10_games(self):

        for i in range(15):
            console = Console.objects.create(name=f'console{i}', to_user=self.user)
            game = Game.objects.create(title=f'game{i}', to_user=self.user)
            console.full_clean()
            console.save()
            game.full_clean()
            game.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['latest_games']), 10)
        self.assertEqual(len(response.context['latest_consoles']), 10)


class GameRatingViewTests(BaseViewTest):
    def test_add_game_rating_authenticated_should_pass(self):
        self.client.login(username='testuser', password='testpass123')
        data = {'rating': 4}
        response = self.client.post(
            reverse('rate_game', kwargs={'game_pk': self.game.pk}),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('message', response_data)
        self.assertEqual(response_data['rating'], 4)

    def test_add_game_rating_unauthenticated_should_redirect_to_login(self):
        data = {'rating': 4}
        response = self.client.post(
            reverse('rate_game', kwargs={'game_pk': self.game.pk}),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)

    def test_add_game_rating_invalid_value_should_return_400(self):
        self.client.login(username='testuser', password='testpass123')
        data = {'rating': 6}  # Invalid rating value
        response = self.client.post(
            reverse('rate_game', kwargs={'game_pk': self.game.pk}),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_get_user_rating_to_game_returns_correctly(self):
        self.client.login(username='testuser', password='testpass123')

        GameRating.objects.create(
            from_user=self.user,
            to_game=self.game,
            rating=4
        )

        response = self.client.get(
            reverse('get_user_rating_to_game', kwargs={'game_pk': self.game.pk})
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['rating'], 4)


class ConsoleRatingViewTests(BaseViewTest):
    def test_add_console_rating_authenticated_should_pass(self):
        self.client.login(username='testuser', password='testpass123')
        data = {'rating': 4}
        response = self.client.post(
            reverse('rate_console', kwargs={'console_pk': self.console.pk}),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('message', response_data)
        self.assertEqual(response_data['rating'], 4)

    def test_add_console_rating_unauthenticated_should_redirect_to_login(self):
        data = {'rating': 4}
        response = self.client.post(
            reverse('rate_console', kwargs={'console_pk': self.console.pk}),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)

    def test_add_console_rating_invalid_value_should_return_400(self):
        self.client.login(username='testuser', password='testpass123')
        data = {'rating': 6}  # Invalid rating value
        response = self.client.post(
            reverse('rate_console', kwargs={'console_pk': self.console.pk}),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_get_user_rating_to_console_returns_correctly(self):
        self.client.login(username='testuser', password='testpass123')
        # Create a rating first
        ConsoleRating.objects.create(
            from_user=self.user,
            to_console=self.console,
            rating=4
        )

        response = self.client.get(
            reverse('get_user_rating_to_console', kwargs={'console_pk': self.console.pk})
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['rating'], 4)


class GameCommentViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.valid_comment_data = {
            'comment': 'Test comment'
        }
        self.test_referer = 'http://testserver/games/1/'

    def test_add_game_comment_authenticated_should_create_persists_and_redirect(self):

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('comment_game', kwargs={'game_pk': self.game.pk}),
            self.valid_comment_data,
            HTTP_REFERER=self.test_referer
        )

        # Check redirect
        self.assertEqual(response.status_code, 302)

        comment = GameComment.objects.order_by('-created_on').first()
        self.assertIn(
            f'http://testserver/games/1/#game-comments-',
            response.url
        )

        # Verify comment was created
        comment = GameComment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.comment, 'Test comment')
        self.assertEqual(comment.to_game, self.game)
        self.assertEqual(comment.from_user, self.user)

    def test_add_game_comment_unauthenticated_should_redirect_to_login(self):
        response = self.client.post(
            reverse('comment_game', kwargs={'game_pk': self.game.pk}),
            self.valid_comment_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)

    def test_add_game_comment_invalid_data_should_set_invalid_form_in_session(self):
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {
            'comment': 'x' * 701  # Exceeds max length
        }
        response = self.client.post(
            reverse('comment_game', kwargs={'game_pk': self.game.pk}),
            invalid_data,
            HTTP_REFERER=self.test_referer
        )

        # Should still redirect but with invalid form data in session
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertTrue('invalid_comment_form' in session)


class ConsoleCommentViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.valid_comment_data = {
            'comment': 'Test comment'
        }
        self.test_referer = 'http://testserver/consoles/1/'

    def test_add_console_comment_authenticated_should_create_persists_and_redirects(self):

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('comment_console', kwargs={'console_pk': self.console.pk}),
            self.valid_comment_data,
            HTTP_REFERER=self.test_referer
        )

        # Check redirect
        self.assertEqual(response.status_code, 302)

        comment = ConsoleComment.objects.order_by('-created_on').first()
        self.assertIn(
            f'http://testserver/consoles/1/#console-comments-',
            response.url
        )
        self.assertIsNotNone(comment)
        self.assertEqual(comment.comment, 'Test comment')
        self.assertEqual(comment.to_console, self.console)
        self.assertEqual(comment.from_user, self.user)

    def test_add_console_comment_unauthenticated_should_redirect_to_login(self):
        response = self.client.post(
            reverse('comment_console', kwargs={'console_pk': self.console.pk}),
            self.valid_comment_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)

    def test_add_console_comment_with_invalid_data_should_set_invalid_form_in_session(self):
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {
            'comment': 'x' * 701  # Exceeds max length
        }
        response = self.client.post(
            reverse('comment_console', kwargs={'console_pk': self.console.pk}),
            invalid_data,
            HTTP_REFERER=self.test_referer
        )

        # Should still redirect but with invalid form data in session
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertTrue('invalid_comment_form' in session)

    def test_console_comment_redirect_patterns_sets_correctly(self):
        self.client.login(username='testuser', password='testpass123')

        # Test redirect with console detail page referer
        response = self.client.post(
            reverse('comment_console', kwargs={'console_pk': self.console.pk}),
            self.valid_comment_data,
            HTTP_REFERER=f'http://testserver/consoles/{self.console.pk}/'
        )
        self.assertIn(f'#console-comments-{self.console.pk}', response.url)

        # Test redirect with different page referer
        response = self.client.post(
            reverse('comment_console', kwargs={'console_pk': self.console.pk}),
            self.valid_comment_data,
            HTTP_REFERER='http://testserver/different-page/'
        )
        self.assertIn(f'#comment-{self.console.pk}', response.url)