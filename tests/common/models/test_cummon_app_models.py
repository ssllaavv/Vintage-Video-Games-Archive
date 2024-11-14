from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.games.models import Game
from games_archive.common.models import ConsoleComment, ConsoleRating, GameComment, GameRating


class ConsoleCommentTests(TestCase):
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

    def test_create_console_comment_valid_data_should_create_and_persists(self):
        comment = ConsoleComment.objects.create(
            comment='Test comment',
            to_console=self.console,
            from_user=self.user
        )
        comment.full_clean()
        comment.save()

        comment = ConsoleComment.objects.get(comment='Test comment')

        self.assertEqual(comment.comment, 'Test comment')
        self.assertEqual(comment.to_console, self.console)
        self.assertEqual(comment.from_user, self.user)

    def test_console_comment_str_representation(self):
        comment = ConsoleComment.objects.create(
            comment='Test comment',
            to_console=self.console,
            from_user=self.user
        )
        comment.full_clean()
        comment.save()

        expected_str = f'Comment {comment.pk} form user {self.user.pk} to console {self.console.pk} {comment.created_on}'
        self.assertEqual(str(comment), expected_str)

    def test_console_comment__more_than_max_length_should_raise(self):
        long_comment = 'x' * 701  # One character more than max length
        comment = ConsoleComment(
            comment=long_comment,
            to_console=self.console,
            from_user=self.user
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_console_comment_ordering(self):
        comment1 = ConsoleComment.objects.create(
            comment='First comment',
            to_console=self.console,
            from_user=self.user
        )
        comment1.full_clean()
        comment1.save()

        comment2 = ConsoleComment.objects.create(
            comment='Second comment',
            to_console=self.console,
            from_user=self.user
        )
        comment2.full_clean()
        comment2.save()

        comments = ConsoleComment.objects.all()
        self.assertEqual(comments[0], comment2)  # Most recent first
        self.assertEqual(comments[1], comment1)


class ConsoleRatingTests(TestCase):
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

    def test_create_console_valid_rating_should_pass_create_and_persists(self):
        rating = ConsoleRating.objects.create(
            rating=5,
            to_console=self.console,
            from_user=self.user
        )
        rating.full_clean()
        rating.save()

        rating = ConsoleRating.objects.first()

        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.to_console, self.console)
        self.assertEqual(rating.from_user, self.user)

    def test__console_rating_str_representation(self):
        rating = ConsoleRating.objects.create(
            rating=4,
            to_console=self.console,
            from_user=self.user
        )
        expected_str = f"4 stars from user {self.user.pk} to console {self.console.pk} (rating pk {rating.pk})"
        self.assertEqual(str(rating), expected_str)

    def test_console_rating_with_invalid_rating_should_raise(self):
        # Test invalid rating value
        rating = ConsoleRating(
            rating=6,  # Greater than MAX_RATING_VALUE
            to_console=self.console,
            from_user=self.user
        )
        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_unique_user_and_console_constraint_rating_should_raise(self):
        rating = ConsoleRating.objects.create(
            rating=4,
            to_console=self.console,
            from_user=self.user
        )
        rating.full_clean()
        rating.save()

        # Attempt to create another rating for the same user and console
        with self.assertRaises(IntegrityError):
            rating_2 = ConsoleRating.objects.create(
                rating=5,
                to_console=self.console,
                from_user=self.user
            )
            rating_2.full_clean()


class GameCommentTests(TestCase):
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

    def test_create_game_comment_with_valid_data_should_create_and_persits(self):
        comment = GameComment.objects.create(
            comment='Test comment',
            to_game=self.game,
            from_user=self.user
        )
        comment.full_clean()
        comment.save()

        comment = GameComment.objects.first()

        self.assertEqual(comment.comment, 'Test comment')
        self.assertEqual(comment.to_game, self.game)
        self.assertEqual(comment.from_user, self.user)

    def test_game_comment_str_representation(self):
        comment = GameComment.objects.create(
            comment='Test comment',
            to_game=self.game,
            from_user=self.user
        )
        comment.full_clean()
        comment.save()

        expected_str = f'Comment {comment.pk} form user {self.user.pk} to game {self.game.pk} {comment.created_on}'
        self.assertEqual(str(comment), expected_str)

    def test_game_comment_with_more_than_max_length_should_raise(self):
        long_comment = 'x' * 701  # One character more than max length
        comment = GameComment(
            comment=long_comment,
            to_game=self.game,
            from_user=self.user
        )

        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_game_comment_ordering(self):
        comment1 = GameComment.objects.create(
            comment='First comment',
            to_game=self.game,
            from_user=self.user
        )
        comment1.full_clean()
        comment1.save()

        comment2 = GameComment.objects.create(
            comment='Second comment',
            to_game=self.game,
            from_user=self.user
        )
        comment2.full_clean()
        comment2.save()

        comments = GameComment.objects.all()
        self.assertEqual(comments[0], comment2)  # Most recent first
        self.assertEqual(comments[1], comment1)


class GameRatingTests(TestCase):
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

    def test_create_game_rating_with_valid_data_should_create_and_persists(self):
        rating = GameRating.objects.create(
            rating=5,
            to_game=self.game,
            from_user=self.user
        )
        rating.full_clean()
        rating.save()

        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.to_game, self.game)
        self.assertEqual(rating.from_user, self.user)

    def test_game_rating_str_representation(self):
        rating = GameRating.objects.create(
            rating=4,
            to_game=self.game,
            from_user=self.user
        )
        rating.full_clean()
        rating.save()

        rating = GameRating.objects.first()

        expected_str = f"4 stars from user {self.user.pk} to game {self.game.pk} (rating pk {rating.pk})"
        self.assertEqual(str(rating), expected_str)

    def test_game_rating_with_invalid_rating_should_raise(self):
        # Test invalid rating value
        rating = GameRating(
            rating=6,  # Greater than MAX_RATING_VALUE
            to_game=self.game,
            from_user=self.user
        )

        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_unique_constraint_user_game_rating_should_raise(self):
        rating = GameRating.objects.create(
            rating=4,
            to_game=self.game,
            from_user=self.user
        )
        rating.full_clean()
        rating.save()

        # Attempt to create another rating for the same user and game
        with self.assertRaises(IntegrityError):
            GameRating.objects.create(
                rating=5,
                to_game=self.game,
                from_user=self.user
            )
