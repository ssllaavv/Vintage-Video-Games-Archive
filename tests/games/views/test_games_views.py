from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from games_archive.games.models import Game, Screenshot, GameReview
from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.settings import LOGIN_URL


class GameListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.game1 = Game.objects.create(
            title='Test Game 1',
            release_year=2023,
            to_user=self.user
        )
        self.game1.full_clean()
        self.game1.save()

        self.game2 = Game.objects.create(
            title='Different Game',
            release_year=2023,
            to_user=self.user
        )
        self.game2.full_clean()
        self.game2.save()

    def test_game_list_view_get_sets_games_in_context_correctly_and_uses_correct_template(self):
        response = self.client.get(reverse('game_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_list.html')
        self.assertIn('games', response.context)
        self.assertEqual(list(response.context['games']), [self.game2, self.game1])  # Ordered by -pk

    def test_game_list_search_returns_correctly(self):

        url = reverse('game_list') + '?search=Different'
        print(url)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['games']), 1)
        self.assertEqual(response.context['games'][0], self.game2)

    def test_game_list_pagination(self):
        # Create 15 more games (17 total)
        for i in range(15):
            game = Game.objects.create(
                title=f'Pagination Game {i}',
                release_year=2023,
                to_user=self.user
            )
            game.full_clean()
            game.save()

        response = self.client.get(reverse('game_list'))
        self.assertEqual(len(response.context['games']), 10)  # First page should have 10 items

        response = self.client.get(reverse('game_list') + '?page=2')
        self.assertEqual(len(response.context['games']), 7)  # Second page should have 7 items


class GameDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.game = Game.objects.create(
            title='Test Game',
            release_year=2023,
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

        self.review = GameReview.objects.create(
            from_user=self.user,
            to_game=self.game,
            content='Test review'
        )
        self.review.full_clean()
        self.review.save()

    def test_game_detail_view_get_hits_correct_template_with_correct_context(self):
        response = self.client.get(reverse('game_detail', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_detail.html')
        self.assertEqual(response.context['game'], self.game)
        self.assertIn('screenshots', response.context)
        self.assertIn('review', response.context)
        self.assertIn('comments', response.context)

    def test_game_detail_view_invalid_game_should_return_404(self):
        response = self.client.get(reverse('game_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class GameCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.console = Console.objects.create(
            name='Test Console',
            to_user=self.user
        )
        self.console.full_clean()
        self.console.save()

        self.test_image_path = os.path.join(os.path.dirname(__file__), 'person.png')

    def test_game_create_view_get_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_form.html')

    def test_game_create_view_post_with_valid_data_should_create_persists_and_redirect(self):
        self.client.force_login(self.user)
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'title': 'New Test Game',
                'release_year': 2023,
                'developer': 'Test Developer',
                'genre': 'Action',
                'description': 'Test description',
                'to_consoles': [self.console.id],
                'cover_image': SimpleUploadedFile(
                    name='person.png',
                    content=image_file.read(),
                    content_type='image/png'
                )
            }
            response = self.client.post(reverse('game_create'), data=form_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Game.objects.count(), 1)
            game = Game.objects.first()
            self.assertEqual(game.title, 'New Test Game')
            self.assertEqual(game.to_user, self.user)

    def test_game_create_view_unauthorized_should_redirect_to_login_and_add_next(self):
        response = self.client.get(reverse('game_create'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
        expected_url = reverse(LOGIN_URL) + '?next=' + reverse('game_create')
        self.assertEqual(expected_url, response.url)


class GameUpdateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.other_user = GamesArchiveUser.objects.create_user(
            username='otheruser',
            password='testpass',
            email='other@user.com'
        )
        self.other_user.full_clean()
        self.other_user.save()

        self.game = Game.objects.create(
            title='Test Game',
            release_year=2023,
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

    def test_game_update_view_get_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_update', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_form.html')

    def test_game_update_view_post_updates_correctly_and_persists(self):
        self.client.force_login(self.user)
        form_data = {
            'title': 'Updated Test Game',
            'release_year': 2024,
        }
        response = self.client.post(
            reverse('game_update', kwargs={'pk': self.game.pk}),
            data=form_data
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.title, 'Updated Test Game')
        self.assertEqual(self.game.release_year, 2024)

    def test_game_update_view_unauthorized_user_should_return_403(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('game_update', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden


class GameDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.other_user = GamesArchiveUser.objects.create_user(
            username='otheruser',
            password='testpass',
            email='other@user.com'
        )
        self.other_user.full_clean()
        self.other_user.save()

        self.game = Game.objects.create(
            title='Test Game',
            release_year=2023,
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

    def test_game_delete_view_get_authorized_should_return_200_and_use_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_delete', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_confirm_delete.html')

    def test_game_delete_view_post_should_delete_and_redirect_correctly(self):

        self.assertEqual(Game.objects.count(), 1)

        self.client.force_login(self.user)
        response = self.client.post(reverse('game_delete', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to success URL
        self.assertEqual(response.url, reverse('game_list'))
        self.assertEqual(Game.objects.count(), 0)

    def test_game_delete_view_unauthorized_user_should_not_delete_and_return_403(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse('game_delete', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertEqual(Game.objects.count(), 1)


class ReviewViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.game = Game.objects.create(
            title='Test Game',
            release_year=2023,
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

    def test_add_review_view_get_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('add_review', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_form.html')

    def test_add_review_view_post_create_persists_and_redirect_correctly(self):
        self.client.force_login(self.user)
        form_data = {
            'content': 'Test review content'
        }
        response = self.client.post(
            reverse('add_review', kwargs={'pk': self.game.pk}),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game_detail', kwargs={'pk': self.game.pk}))
        self.assertEqual(GameReview.objects.count(), 1)

        print(response.url)

    def test_delete_review_view_should_delete_and_redirect_correctly(self):
        review = GameReview.objects.create(
            from_user=self.user,
            to_game=self.game,
            content='Test review'
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_review', kwargs={'pk': self.game.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game_detail', kwargs={'pk': self.game.pk}))
        self.assertEqual(GameReview.objects.count(), 0)

        print(response.url)


class ScreenshotViewTests(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        self.game = Game.objects.create(
            title='Test Game',
            release_year=2023,
            to_user=self.user
        )
        self.game.full_clean()
        self.game.save()

        self.test_image_path = os.path.join(os.path.dirname(__file__), 'person.png')

    def test_add_screenshot_view_creates_persists_and_redirects(self):
        self.client.force_login(self.user)
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'picture': SimpleUploadedFile(
                    name='person.png',
                    content=image_file.read(),
                    content_type='image/png'
                )
            }
            response = self.client.post(
                reverse('add_screenshot', kwargs={'pk': self.game.pk}),
                data=form_data,
                HTTP_REFERER=f'/games/{self.game.pk}/'
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Screenshot.objects.count(), 1)

    def test_delete_screenshot_view_deletes_and_return_200(self):

        self.client.force_login(self.user)
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'picture': SimpleUploadedFile(
                    name='person.png',
                    content=image_file.read(),
                    content_type='image/png'
                )
            }
            response = self.client.post(
                reverse('add_screenshot', kwargs={'pk': self.game.pk}),
                data=form_data,
                HTTP_REFERER=f'/games/{self.game.pk}/'
            )
            screenshot = Screenshot.objects.first()
            screenshot.full_clean()
            screenshot.save()

            self.assertEqual(Screenshot.objects.count(), 1)

            response = self.client.post(reverse('delete_screenshot', kwargs={'pk': screenshot.pk}))
            self.assertEqual(response.status_code, 200)  # Returns JSON response
            self.assertEqual(Screenshot.objects.count(), 0)

