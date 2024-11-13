import os

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console, Supplier
from games_archive.custom_widgets import CustomImageUploadWidget
from games_archive.games.forms import GameForm, ScreenshotForm, GameReviewForm, GameSearchForm
from games_archive.games.models import Game, Screenshot, GameReview

User = get_user_model()


class GameFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='user@user.com'
        )
        self.user.full_clean()
        self.user.save()

        # Create a test console
        self.console = Console.objects.create(
            name='Test Console',
            to_user=self.user,
        )
        self.console.full_clean()
        self.console.save()

        # Setup test image path
        self.test_image_path = os.path.join(os.path.dirname(__file__), 'person.png')
        self.assertTrue(
            os.path.exists(self.test_image_path),
            f"Test image not found at {self.test_image_path}"
        )

    def test_game_form_valid_data_should_pass(self):
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'title': 'Test Game',
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

            form = GameForm(data=form_data, files=form_data)
            self.assertTrue(form.is_valid())

    def test_game_form_with_invalid_data_should_raise(self):
        form_data = {
            'title': 'a',
            'release_year': 1939,
            'cover_image': SimpleUploadedFile('cover.jpg', b'x' * (5 * 1024 * 1024 + 1)),
        }
        form = GameForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('release_year', form.errors)
        self.assertIn('cover_image', form.errors)

    def test_game_form_missing_required_fields_title_should_raise(self):
        form_data = {}  # Empty data
        form = GameForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)  # Title is required

    def test_game_form_invalid_release_year_should_raise(self):
        form_data = {
            'title': 'Test Game',
            'release_year': 3000,  # Future year, should be invalid
        }
        form = GameForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('release_year', form.errors)

    def test_game_form_create_view_should_create_persist_and_andRedirect(self):
        self.client.force_login(self.user)
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'title': 'Test Game',
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

            created_game = Game.objects.first()
            self.assertEqual(created_game.genre, 'Action')
            self.assertEqual(created_game.title, 'Test Game')
            self.assertEqual(response.status_code, 302)  # Should redirect


class ScreenshotFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create_user(username='testuser', password='testpass', email='user@user.com')
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

        self.assertTrue(
            os.path.exists(self.test_image_path),
            f"Test image not found at {self.test_image_path}"
        )

    def test_screenshot_form_valid_data_should_pass(self):
        with open(self.test_image_path, 'rb') as image_file:
            form_data = {
                'to_game': self.game.id,
                'picture': SimpleUploadedFile(
                    name='person.png',
                    content=image_file.read(),
                    content_type='image/png'
                )
            }
            form = ScreenshotForm(data=form_data, files=form_data)
            # print(f"Picture: {form.fields['picture'].__dict__}")
            self.assertTrue(form.is_valid())

    def test_screenshot_form_missing_picture_should_raise(self):
        form_data = {
            'to_game': self.game.id
        }
        form = ScreenshotForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('picture', form.errors)

    def test_screenshot_form_create_persists_and_redirect(self):
        with open(self.test_image_path, 'rb') as image_file:
            # Create the form data properly combining both form_data and files into a single dictionary
            form_data = {
                'picture': SimpleUploadedFile(
                    name='person.png',
                    content=image_file.read(),
                    content_type='image/png'
                )
            }

            # Login user
            self.client.force_login(self.user)

            # Get the URL using reverse
            url = reverse('add_screenshot', kwargs={'pk': self.game.pk})

            # Make the POST request with a single form_data dictionary
            response = self.client.post(
                url,
                data=form_data,
                HTTP_REFERER=f'http://testserver/games/{self.game.pk}/'
            )

            # Check redirect
            self.assertEqual(response.status_code, 302)  # Should redirect

            # Verify screenshot was created
            self.assertEqual(Screenshot.objects.count(), 1)
            screenshot = Screenshot.objects.first()
            self.assertEqual(screenshot.to_game, self.game)
            self.assertEqual(screenshot.from_user, self.user)
            self.assertTrue(screenshot.picture)
            self.assertIn('game_screenshots/person', screenshot.picture.name)

            # Check if the redirect URL contains the screenshot ID
            self.assertIn(f'screenshot-{screenshot.pk}', response.url)

            # Follow the redirect
            response = self.client.get(response.url)
            self.assertEqual(response.status_code, 200)


class GameReviewFormTests(TestCase):
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

    def test_review_form_valid_data_should_pass(self):
        form_data = {
            'content': 'This is a test review content.'
        }
        form = GameReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_empty_content_should_raise(self):
        form_data = {
            'content': ''
        }
        form = GameReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_review_form_too_long_content_should_raise(self):
        form_data = {
            'content': 'x' * 2501  # Max length is 2500
        }
        form = GameReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_review_form_create_view_should_create_persist_and_redirect(self):
        self.client.force_login(self.user)
        form_data = {
            'content': 'This is a test review content.'
        }

        response = self.client.post(
            reverse('add_review', kwargs={'pk': self.game.pk}),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(GameReview.objects.count(), 1)


class GameSearchFormTests(TestCase):
    def setUp(self):
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

    def test_search_form_valid_data_should_pass(self):
        form_data = {
            'search': 'Test Game'
        }
        form = GameSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_empty_search_should_pass(self):
        form_data = {
            'search': ''
        }
        form = GameSearchForm(data=form_data)
        self.assertTrue(form.is_valid())  # Empty search is allowed

    def test_search_form_in_list_view_should_sett_search_query_in_request(self):
        response = self.client.get(reverse('game_list'), {'search': 'Test Game'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')

    def test_search_form_no_results(self):
        response = self.client.get(reverse('game_list'), {'search': 'Nonexistent Game'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Game')
