from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from games_archive.consoles.models import Console, Supplier
from games_archive.games.models import Game, Screenshot, GameReview

User = get_user_model()


class GameModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='user@user.com')
        self.console = Console.objects.create(name='Nintendo Switch', to_user=self.user)

        self.user.full_clean()
        self.console.full_clean()

    def test_game_creation_with_valid_data_and_data_persists(self):
        game = Game.objects.create(
            title='Super Mario Odyssey',
            release_year=2017,
            developer='Nintendo',
            genre='Action-adventure',
            description='Explore a variety of landscapes as Mario and Cappy.',
            cover_image=SimpleUploadedFile('cover.jpg', b'content'),
            to_user=self.user
        )
        game.to_consoles.add(self.console)
        game.full_clean()
        pk = game.pk

        game = Game.objects.get(pk=pk)

        self.assertEqual(game.title, 'Super Mario Odyssey')
        self.assertEqual(game.release_year, 2017)
        self.assertEqual(game.developer, 'Nintendo')
        self.assertEqual(game.genre, 'Action-adventure')
        self.assertEqual(game.description, 'Explore a variety of landscapes as Mario and Cappy.')
        self.assertIsNotNone(game.cover_image)
        self.assertEqual(list(game.to_consoles.all()), [self.console])
        self.assertEqual(game.to_user, self.user)

    def test_game_creation_with_invalid_title_should_raise(self):
        with self.assertRaises(ValidationError):
            game = Game.objects.create(
                title='a',
                to_user=self.user
            )
            game.full_clean()

    def test_game_creation_with_invalid_release_year_should_raise(self):
        with self.assertRaises(ValidationError):
            game = Game.objects.create(
                title='Super Mario Odyssey',
                release_year=1939,
                to_user=self.user
            )
            game.full_clean()

    def test_game_creation_with_invalid_file_size_should_raise(self):
        with self.assertRaises(ValidationError):
            game = Game.objects.create(
                title='Super Mario Odyssey',
                cover_image=SimpleUploadedFile('cover.jpg', b'x' * (5 * 1024 * 1024 + 1)),
                to_user=self.user
            )
            game.full_clean()

    def test_game_rating_property_returns_correctly(self):
        game = Game.objects.create(
            title='Super Mario Odyssey',
            to_user=self.user
        )
        game.full_clean()

        self.assertEqual(game.rating, 0)

        user2 = User.objects.create_user(username='testuser2', password='testpass2', email='user2@user.com')
        user2.full_clean()

        game.gamerating_set.create(rating=4, from_user=self.user)
        game.gamerating_set.create(rating=5, from_user=user2)
        self.assertEqual(game.rating, 4.5)

    def test_game_stars_rating_html_property_returns(self):
        game = Game.objects.create(
            title='Super Mario Odyssey',
            to_user=self.user
        )
        game.full_clean()

        self.assertIsNotNone(game.stars_rating_html)

    def test_game_default_image_property_returns_correctly(self):
        game = Game.objects.create(
            title='Super Mario Odyssey',
            to_user=self.user
        )
        self.assertEqual(game.default_image, Game.DEFAULT_IMAGE)

        game.cover_image = SimpleUploadedFile('cover.jpg', b'content')
        game.full_clean()
        game.save()
        self.assertNotEqual(game.default_image, Game.DEFAULT_IMAGE)


class ScreenshotModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='user@user.com')
        self.user.full_clean()

        self.game = Game.objects.create(
            title='Super Mario Odyssey',
            to_user=self.user
        )
        self.game.full_clean()

    def test_screenshot_creation_with_valid_data_and_data_persists(self):
        screenshot = Screenshot(
            to_game=self.game,
            from_user=self.user,
            picture=SimpleUploadedFile('screenshot.jpg', b'content')
        )
        screenshot.full_clean()
        screenshot.save()

        self.assertEqual(screenshot.to_game, self.game)
        self.assertEqual(screenshot.from_user, self.user)
        self.assertIsNotNone(screenshot.picture)
        self.assertIsNotNone(screenshot.slug)

    def test_screenshot_creation_with_invalid_file_size(self):
        with self.assertRaises(ValidationError):
            screenshot = Screenshot(
                to_game=self.game,
                from_user=self.user,
                picture=SimpleUploadedFile('screenshot.jpg', b'x' * (5 * 1024 * 1024 + 1))
            )
            screenshot.full_clean()
            screenshot.save()


class GameReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='user@user.com')
        self.user.full_clean()

        self.game = Game.objects.create(
            title='Super Mario Odyssey',
            to_user=self.user
        )
        self.game.full_clean()

    def test_game_review_creation_with_valid_data_and_data_persists(self):
        review = GameReview(
            from_user=self.user,
            to_game=self.game,
            content='Great game!'
        )
        review.full_clean()
        review.save()

        self.assertEqual(review.from_user, self.user)
        self.assertEqual(review.to_game, self.game)
        self.assertEqual(review.content, 'Great game!')

    def test_game_review_creation_with_invalid_content_should_raise(self):
        with self.assertRaises(ValidationError):
            review = GameReview(
                from_user=self.user,
                to_game=self.game,
                content='a' * 2501
            )
            review.full_clean()
            review.save()
