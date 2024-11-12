
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from games_archive.accounts.models import GamesArchiveUser


class GamesArchiveUserModelTest(TestCase):
    def setUp(self):
        # Sample valid data for testing
        self.valid_user_data = {
            'first_name': 'john',
            'last_name': 'doe',
            'email': 'john.doe@example.com',
            'profile_picture': SimpleUploadedFile('profile_pic.jpg', b'file_content'),
            'gender': 'Male',  # assuming gender is a CharField or ChoiceField
            'age': 25,
            'username': 'username',
            'password': 'password',
        }

    def test_create_valid_user_should_pass(self):

        user = GamesArchiveUser.objects.create_user(**self.valid_user_data)
        try:
            user.full_clean()  # Validates all fields including custom validators
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for valid data.")

        user.save()

        self.assertNotEqual(user.password, 'password')

        self.assertEqual(user.username, 'username')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.gender, 'Male')
        self.assertEqual(user.age, 25)

        self.assertEqual(GamesArchiveUser.objects.count(), 1)

    def test_first_name_less_than_2_symbols_should_raise(self):

        invalid_user_date = self.valid_user_data
        invalid_user_date['first_name'] = 'a'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_first_name_include_not_letters_should_raise(self):

        invalid_user_date = self.valid_user_data
        invalid_user_date['first_name'] = 's@a'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

        invalid_user_date['first_name'] = '3sa'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_last_name_less_than_2_symbols_should_raise(self):

        invalid_user_date = self.valid_user_data
        invalid_user_date['last_name'] = 'a'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_last_name_include_not_letters_should_raise(self):
        invalid_user_date = self.valid_user_data
        invalid_user_date['last_name'] = 's@a'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

        invalid_user_date['last_name'] = '3sa'

        user = GamesArchiveUser(**self.valid_user_data, )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_profile_picture_size_above_5m_should_raise(self):
        large_file = SimpleUploadedFile('large_file.jpg', b'a' * (5 * 1024 * 1024 + 2))  # File just over 5MB

        invalid_user_date = self.valid_user_data
        invalid_user_date['profile_picture'] = large_file

        user = GamesArchiveUser.objects.create_user(**self.valid_user_data)

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_age_not_in_valid_range_should_raise(self):

        invalid_user_date = self.valid_user_data
        invalid_user_date['age'] = -2

        user = GamesArchiveUser(**invalid_user_date)
        with self.assertRaises(ValidationError):
            user.full_clean()

        invalid_user_date['age'] = 152

        user = GamesArchiveUser(**invalid_user_date)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_gender_Not_in_Select_options_should_raise(self):

        invalid_user_data = self.valid_user_data
        invalid_user_data['gender'] = 'X'

        user = GamesArchiveUser(**invalid_user_data)
        with self.assertRaises(ValidationError):
            user.full_clean()
