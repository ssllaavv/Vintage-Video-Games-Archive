import os

from django.core.files import File
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class UserRegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.home_url = reverse('home')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_register_page_loads_successfully_should_pass(self):
        """Test that register page loads with a GET request"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_successful_registration_create_user_and_login(self):
        """Test successful user registration with valid data"""
        response = self.client.post(self.register_url, self.valid_user_data)

        # Check user was created
        self.assertTrue(get_user_model().objects.filter(username='testuser').exists())

        # Check user is logged in
        user = get_user_model().objects.get(username='testuser')
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # Check redirect to home page
        self.assertRedirects(response, self.home_url)

    def test_invalid_registration_should_return_form_errors_and_not_register_user(self):
        """Test registration with invalid data"""
        invalid_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'different',
        }
        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(get_user_model().objects.filter(username='testuser').exists())

    def test_next_parameter_redirect(self):
        """Test redirect to 'next' parameter after successful registration"""
        next_url = '/some-valid-url/'
        post_data = self.valid_user_data.copy()
        post_data['next'] = next_url

        response = self.client.post(self.register_url, post_data)
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_next_parameter_with_register_redirects_to_home(self):
        """Test that 'next' parameter containing 'register' redirects to home"""
        post_data = self.valid_user_data.copy()
        post_data['next'] = '/register/something'

        response = self.client.post(self.register_url, post_data)
        self.assertRedirects(response, self.home_url)

    def test_next_parameter_none_redirects_to_home(self):
        """Test that None 'next' parameter redirects to home"""
        post_data = self.valid_user_data.copy()
        post_data['next'] = 'None'

        response = self.client.post(self.register_url, post_data)
        self.assertRedirects(response, self.home_url)

    def test_register_with_existing_username_should_not_create_user_and_return_invalid_form(self):
        """Test registration with already existing username"""
        # Create a user first
        get_user_model().objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='ExistingPass123!'
        )

        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(get_user_model().objects.filter(username='testuser').count(), 1)

    def test_register_with_existing_email_should_not_create_user_and_return_invalid_form(self):
        """Test registration with already existing email"""
        # Create a user first
        get_user_model().objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='ExistingPass123!'
        )

        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(get_user_model().objects.filter(email='test@example.com').count(), 1)


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_login_page_loads_successfully(self):
        """Test that login page loads with a GET request"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login_and_session_created(self):
        """Test successful login with valid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_invalid_login_returns_form_with_errors_and_session_not_created(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_next_parameter_redirect_correctly(self):
        """Test redirect to 'next' parameter after successful login"""
        next_url = '/some-valid-url/'
        response = self.client.post(
            f'{self.login_url}?next={next_url}',
            {
                'username': 'testuser',
                'password': 'TestPass123!',
                'next': next_url
            }
        )
        self.assertRedirects(response, next_url, fetch_redirect_response=False)


class UserLogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_logout_redirects_to_login(self):
        """Test that logout redirects to login page"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logs_out_and_remove_session(self):
        """Test that GET request to logout also works"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)


class UserEditViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')
        self.edit_url = reverse('profile edit', kwargs={'pk': self.user.pk})

    def test_edit_page_loads_successfully(self):
        """Test that edit page loads with a GET request"""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_edit.html')

    def test_successful_profile_update_and_redirect_to_profile_details(self):
        """Test successful profile update with valid data"""
        response = self.client.post(self.edit_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'gender': 'Male',
            'age': 25
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john@example.com')
        self.assertRedirects(response,
                           reverse('profile details', kwargs={'pk': self.user.pk}))

    def test_invalid_profile_update_returns_form_with_errors(self):
        """Test profile update with invalid data"""
        response = self.client.post(self.edit_url, {
            'first_name': 'John123',  # Invalid name with numbers
            'email': 'invalid-email',  # Invalid email format
            'age': 200  # Age too high
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


class UserDetailViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='John',
            last_name='Doe'
        )
        self.client = Client()
        self.detail_url = reverse('profile details', kwargs={'pk': self.user.pk})

    def test_detail_page_loads_successfully(self):
        """Test that detail page loads with a GET request"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile-details.html')

    def test_context_data_includes_all_data(self):
        """Test that context contains required data"""
        response = self.client.get(self.detail_url)
        self.assertIn('comments_count', response.context)
        self.assertIn('rates', response.context)
        self.assertIn('games', response.context)
        self.assertIn('is_paginated', response.context)

    def test_user_details_displayed_correctly(self):
        """Test that user details are displayed correctly"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.context['object'], self.user)
        self.assertEqual(response.context['object'].get_user_name(), 'John Doe')


class UserDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')
        self.delete_url = reverse('profile delete', kwargs={'pk': self.user.pk})

    def test_delete_page_loads_successfully(self):
        """Test that delete page loads with a GET request"""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile-delete.html')

    def test_successful_profile_deletion(self):
        """Test successful profile deletion"""
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())

    def test_login_required_for_deletion(self):
        """Test that login is required for deletion"""
        self.client.logout()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())