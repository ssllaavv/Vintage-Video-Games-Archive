
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.storage import default_storage
import os

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.models import Console
from games_archive.consoles.forms import ConsoleForm
from games_archive.settings import LOGIN_URL


class ConsoleViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test users
        self.user = GamesArchiveUser.objects.create(
            username='testuser',
            email='user@email.com'
        )
        self.user.set_password('userpass')
        self.user.full_clean()
        self.user.save()

        self.staff_user = GamesArchiveUser.objects.create(
            username='staffuser',
            email='staff@email.com',
            is_staff=True
        )
        self.staff_user.set_password('staffpass')
        self.staff_user.full_clean()
        self.staff_user.save()

        # Setup test image
        self.test_image_path = os.path.join(os.path.dirname(__file__), 'person.png')
        self.assertTrue(os.path.exists(self.test_image_path))

        # Create a test console
        with open(self.test_image_path, 'rb') as img:
            self.console = Console.objects.create(
                name='Test Console',
                manufacturer='Test Manufacturer',
                release_year=2022,
                description='Test Description',
                cover_image=SimpleUploadedFile(
                    name='test_image.png',
                    content=img.read(),
                    content_type='image/png'
                ),
                to_user=self.user
            )
            self.console.full_clean()
            self.console.save()

    def tearDown(self):
        # Clean up uploaded files
        if self.console.cover_image:
            if default_storage.exists(self.console.cover_image.name):
                default_storage.delete(self.console.cover_image.name)
        if self.console.logo:
            if default_storage.exists(self.console.logo.name):
                default_storage.delete(self.console.logo.name)

    def test_console_list_view_uses_correct_template_Sets_context_correctly_and_return_200(self):
        # Test basic list view
        response = self.client.get(reverse('console_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'console_list.html')
        self.assertIn('consoles', response.context)
        self.assertIn('search_form', response.context)

    def test_console_list_view_with_search_query(self):
        response = self.client.get(reverse('console_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consoles']), 1)
        self.assertEqual(response.context['search_query'], 'Test')

        response = self.client.get(reverse('console_list'), {'search': 'not_existing'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consoles']), 0)
        self.assertEqual(response.context['search_query'], 'not_existing')

    def test_console_detail_view_uses_correct_template_sets_context_and_return_200(self):
        response = self.client.get(reverse('console_detail', kwargs={'pk': self.console.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'console_detail.html')
        self.assertEqual(response.context['console'], self.console)
        for item in ['console', 'comments', 'console_comment_form', 'popular_games']:
            self.assertIn(item, response.context)

    def test_console_detail_view_invalid_pk_should_return_404(self):
        response = self.client.get(reverse('console_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_console_create_view_unauthorized_redirects_to_login_with_next_set(self):
        create_url = reverse('console_create')

        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertIn(LOGIN_URL, response.url)
        self.assertIn('?next=/consoles/add/',  response.url)
        # print(response.url)

    def test_console_create_view_authorized_uses_correct_template_return_200_create_and_persists(self):
        create_url = reverse('console_create')
        #
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'console_form.html')

        # Test valid console creation
        with open(self.test_image_path, 'rb') as img:
            form_data = {
                'name': 'New Console',
                'manufacturer': 'New Manufacturer',
                'release_year': 2023,
                'description': 'New Description',
                'cover_image': SimpleUploadedFile(
                    name='new_image.png',
                    content=img.read(),
                    content_type='image/png'
                )
            }
            response = self.client.post(create_url, data=form_data)
            self.assertEqual(Console.objects.count(), 2)
            new_console = Console.objects.get(name='New Console')
            self.assertEqual(new_console.to_user, self.user)

    def test_console_update_view_anonymous_should_redirect_with_next_set(self):
        update_url = reverse('console_update', kwargs={'pk': self.console.pk})

        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)
        self.assertIn(f'?next=/consoles/{self.console.pk}/edit', response.url)

    def test_console_update_view_unauthorized_should_403(self):
        update_url = reverse('console_update', kwargs={'pk': self.console.pk})

        other_user = GamesArchiveUser.objects.create_user(
            username='otheruser',
            email='other@user.com'
        )
        other_user.set_password('other_pass')
        other_user.full_clean()
        other_user.save()

        self.client.login(username='otheruser', password='other_pass')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_console_update_view_valid_update_should_pass(self):
        update_url = reverse('console_update', kwargs={'pk': self.console.pk})

        # Test owner access
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'console_form.html')

        # Test valid update
        with open(self.test_image_path, 'rb') as img:
            update_data = {
                'name': 'Updated Console',
                'manufacturer': 'Updated Manufacturer',
                'release_year': 2024,
                'description': 'Updated Description',
                'cover_image': SimpleUploadedFile(
                    name='updated_image.png',
                    content=img.read(),
                    content_type='image/png'
                )
            }
            response = self.client.post(update_url, data=update_data)
            updated_console = Console.objects.get(pk=self.console.pk)
            self.assertEqual(updated_console.name, 'Updated Console')

    def test_console_update_view_with_staff_user_should_access_it(self):
        update_url = reverse('console_update', kwargs={'pk': self.console.pk})

        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

    def test_console_delete_view_anonymous_should_redirect_to_login(self):
        delete_url = reverse('console_delete', kwargs={'pk': self.console.pk})

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(LOGIN_URL, response.url)

    def test_console_delete_view_not_staff_should_return_403(self):
        delete_url = reverse('console_delete', kwargs={'pk': self.console.pk})

        self.client.login(username='testuser', password='userpass')
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_console_delete_view_staff_should_pass_and_return_confirm_template(self):
        delete_url = reverse('console_delete', kwargs={'pk': self.console.pk})

        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'console_confirm_delete.html')

    def test_console_delete_view_actual_delete_staff_should_pass_and_redirect_correctly(self):
        delete_url = reverse('console_delete', kwargs={'pk': self.console.pk})

        self.client.login(username='staffuser', password='staffpass')

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)  # Redirects to success URL
        self.assertEqual(response.url, '/consoles/')
        self.assertEqual(Console.objects.count(), 0)

    def test_pagination(self):
        """Test list view pagination"""
        # Create 15 consoles (10 per page)
        for i in range(15):
            Console.objects.create(
                name=f'Console {i}',
                manufacturer='Test Manufacturer',
                release_year=2022,
                to_user=self.user
            )

        # Test first page
        response = self.client.get(reverse('console_list'))
        self.assertEqual(len(response.context['consoles']), 10)
        self.assertTrue(response.context['is_paginated'])

        # Test second page
        response = self.client.get(reverse('console_list'), {'page': 2})
        self.assertEqual(len(response.context['consoles']), 6)  # 5 + 1 from setUp