from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError

from games_archive.accounts.models import GamesArchiveUser
from games_archive.common.models import ConsoleRating
from games_archive.consoles.models import Console, Supplier


class TestConsoleModel(TestCase):
    def setUp(self):
        self.user = GamesArchiveUser.objects.create(
            username='testuser',
            email='user@user.com'
        )
        self.user.set_password('pass')
        self.user.full_clean()
        self.user.save()

        self.second_user = GamesArchiveUser.objects.create(
            username='testuser2',
            email='user2@user.com'
        )
        self.second_user.set_password('pass2')
        self.second_user.full_clean()
        self.second_user.save()

    def test_console_create_with_name_Len_1_should_raise(self):
        with self.assertRaises(ValidationError):
            console = Console.objects.create(name='T', manufacturer='Test', release_year=2022, to_user=self.user)
            console.full_clean()

    def test_console_create_with_invalid_release_year_should_raise(self):
        with self.assertRaises(ValidationError):
            console = Console.objects.create(name='Teo', manufacturer='Test2', release_year=1888, to_user=self.user)
            console.full_clean()

        with self.assertRaises(ValidationError):
            console = Console.objects.create(name='Teo2', manufacturer='Test3', release_year=2025, to_user=self.user)
            console.full_clean()

    def test_console_default_image(self):
        console = Console.objects.create(
            name='Test Console', manufacturer='Test Manufacturer', release_year=2022, to_user=self.user
        )
        console.full_clean()
        console.save()
        self.assertEqual(console.default_image, Console.DEFAULT_IMAGE)

    def test_console_rating_property_when_no_rating_should_be_zero(self):
        console = Console.objects.create(
            name='Test Console', manufacturer='Test Manufacturer', release_year=2022, to_user=self.user
        )
        console.full_clean()
        console.save()

        self.assertEqual(console.rating, 0)

    def test_console_rating_property_two_ratings_should_be_average(self):
        console = Console.objects.create(
            name='Test Console', manufacturer='Test Manufacturer', release_year=2022, to_user=self.user
        )
        console.full_clean()
        console.save()

        rating_1 = ConsoleRating.objects.create(
            rating=4,
            from_user=self.user,
            to_console=console
        )
        rating_1.full_clean()
        rating_1.save()

        rating_2 = ConsoleRating.objects.create(
            rating=5,
            from_user=self.second_user,
            to_console=console
        )
        rating_2.full_clean()
        rating_2.save()

        self.assertEqual(console.rating, 4.5)

    def test_console_image_upload_logo_and_cover_image_with_valid_size_should_pass(self):
        image_file = SimpleUploadedFile("test_image.jpg", b"content", content_type="image/jpeg")
        console = Console.objects.create(
            name='Test Console',
            manufacturer='Test Manufacturer',
            release_year=2022,
            to_user=self.user,
            cover_image=image_file,
            logo=image_file
        )
        console.full_clean()
        console.save()

        self.assertIsNotNone(console.cover_image)
        self.assertEqual(console.cover_image.size, len(b"content"))
        self.assertIsNotNone(console.logo)
        self.assertIn('test_image', console.logo.name)
        self.assertEqual(console.logo.size, len(b"content"))

    def test_console_image_upload_invalid_size(self):
        with self.assertRaises(ValidationError):
            invalid_image_file = SimpleUploadedFile(
                "test_image.jpg", b"*" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
            )
            console = Console.objects.create(
                name='Test Console', manufacturer='Test Manufacturer',
                release_year=2022, to_user=self.user, cover_image=invalid_image_file
            )
            console.full_clean()
            console.save()

    def test_console_unique_name_constraint_should_raise(self):
        console_1 = Console.objects.create(
            name='Test Console',
            manufacturer='Test Manufacturer',
            release_year=2022,
            to_user=self.user
        )
        console_1.full_clean()
        console_1.save()

        with self.assertRaises(IntegrityError):
            console_2 = Console.objects.create(
                name='tEst cOnsoLe',
                manufacturer='Another Manufacturer',
                release_year=2023,
                to_user=self.second_user
            )
            console_2.full_clean()
            console_2.save()

    def test_supplier_create_without_image_should_raise(self):
        supplier = Supplier.objects.create(name='Test Supplier', logo=None)
        with self.assertRaises(ValidationError):
            supplier.full_clean()
            supplier.save()

    def test_supplier_create_with_valid_data_should_create_and_persists(self):
        image_file = SimpleUploadedFile(
            "test_image.jpg", b"*" * (5 * 1024 * 1024 + 10), content_type="image/jpeg"
        )
        supplier = Supplier.objects.create(name='Test Supplier', logo=image_file)
        supplier.full_clean()
        supplier.save()

        self.assertEqual(supplier.name, 'Test Supplier')
        self.assertEqual(supplier.logo.size, (5 * 1024 * 1024 + 10))
        self.assertEqual(Supplier.objects.count(), 1)










