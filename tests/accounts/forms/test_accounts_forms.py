from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory


from games_archive.accounts.forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from games_archive.accounts.models import GamesArchiveUser


class UserRegistrationFormTests(TestCase):
    def setUp(self):
        self.valid_form_data = {
            'username': 'username',
            'email': 'email@email.com',
            'password1': 'VeryStrongPass@!34',
            'password2': 'VeryStrongPass@!34'
        }

    def test_register_valid_user_should_pass(self):
        data = self.valid_form_data
        form = UserRegistrationForm(data)

        self.assertTrue(form.is_valid())

    def test_register_user_with_different_pass1_and_pass2_should_raise(self):
        data = self.valid_form_data
        data['password2'] = 'pass2'
        form = UserRegistrationForm(data)

        self.assertFalse(form.is_valid())


class UserLoginFormTests(TestCase):
    def setUp(self):
        self.user = GamesArchiveUser.objects.create_user(
            username='username',
            email='email@email.com',
        )

        self.user.set_password('pass')
        self.user.full_clean()
        self.user.save()

        self.valid_login_data = {
            'username': 'username',
            'password': 'pass',
        }

        # Create a request object
        self.factory = RequestFactory()

    def test_login_with_valid_user_login_data_should_pass(self):
        request = self.factory.post('/login/', data=self.valid_login_data)

        # Pass the request to the form
        form = UserLoginForm(request=request, data=self.valid_login_data)

        # if not form.is_valid():
        #     print("Form errors:", form.errors)

        self.assertTrue(form.is_valid())

    def test_login_with_invalid_user_login_data_should_raise(self):
        data = {
            'username': 'username',
            'password': 'pass1',
        }

        request = self.factory.post('/login/', data=data)

        # Pass the request to the form
        form = UserLoginForm(request=request, data=data)

        # if not form.is_valid():
        #     print("Form errors:", form.errors)

        self.assertFalse(form.is_valid())

    def test_login_form_sets_attrs_correctly(self):
        form = UserLoginForm()

        result = form.fields['username'].widget.attrs.get('placeholder', None)
        expected = 'Username'

        self.assertEqual(expected, result)

        result = form.fields['password'].widget.attrs.get('placeholder', None)
        expected = 'Password'

        self.assertEqual(expected, result)

        result = form.fields['username'].widget.attrs.get('autofocus', None)
        expected = True

        self.assertEqual(expected, result)

        result = form.fields['password'].widget.attrs.get('autocomplete', None)
        expected = 'current-password'

        self.assertEqual(expected, result)


class UserProfileFormTests(TestCase):
    def setUp(self):
        self.valid_user_data = {
            'first_name': 'john',
            'last_name': 'doe',
            'email': 'john.doe@example.com',
            'profile_picture': SimpleUploadedFile('profile_pic.jpg', b'file_content'),
            'gender': 'Male',  # assuming gender is a CharField or ChoiceField
            'age': 25,
        }

        # self.user = GamesArchiveUser.objects.create_user(**self.valid_user_data)
        #
        # self.user.full_clean()
        # self.user.save()

    def test_UserProfileForm_with_valid_data_should_pass(self):
        form = UserProfileForm(self.valid_user_data)

        self.assertTrue(form.is_valid())

    def test_UserProfileForm_with_invalid_data_should_raise(self):
        data = self.valid_user_data
        data['first_name'] = 'j'

        form = UserProfileForm(data)

        self.assertFalse(form.is_valid())

    def test_UserProfileForm_fields_are_correct_should_pass(self):
        form = UserProfileForm()

        expected = ['first_name', 'last_name', 'email', 'gender', 'age', 'profile_picture']
        result = list(form.fields)
        self.assertEqual(expected, result)

    def test_if_profile_picture_uses_correct_widget_should_pass(self):
        form = UserProfileForm()

        expected = 'CustomImageUploadWidget'
        result = form.fields['profile_picture'].widget.__class__.__name__

        self.assertEqual(expected, result)
