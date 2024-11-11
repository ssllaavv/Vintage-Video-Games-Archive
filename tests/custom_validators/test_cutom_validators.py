from django.core.exceptions import ValidationError
from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile

from games_archive.custom_validators import validate_name_is_longer_than_2_characters, \
    validate_name_contains_only_letters, validate_name, validate_file_size, validate_year_less_than_current_year, \
    validate_year_more_than_1940r, validate_release_year


class TestCustomValidators(TestCase):
    def test_validate_name_is_longer_than_2_characters(self):
        with self.assertRaises(ValidationError):
            validate_name_is_longer_than_2_characters('J')

    def test_validate_name_contains_only_letters(self):
        with self.assertRaises(ValidationError):
            validate_name_contains_only_letters('John123')

    def test_validate_name(self):
        validate_name('John')
        with self.assertRaises(ValidationError):
            validate_name('J')
        with self.assertRaises(ValidationError):
            validate_name('John123')

    def test_validate_file_size(self):
        with self.assertRaises(ValidationError):
            validate_file_size(SimpleUploadedFile(name='test.txt', content=b'A' * (5 * 1024 * 1024 + 1), content_type='text/plain'))

    def test_validate_year_less_than_current_year(self):
        with self.assertRaises(ValidationError):
            validate_year_less_than_current_year(2025)

    def test_validate_year_more_than_1940(self):
        with self.assertRaises(ValidationError):
            validate_year_more_than_1940r(1939)

    def test_validate_release_year(self):
        validate_release_year(2022)
        with self.assertRaises(ValidationError):
            validate_release_year(2025)
        with self.assertRaises(ValidationError):
            validate_release_year(1939)