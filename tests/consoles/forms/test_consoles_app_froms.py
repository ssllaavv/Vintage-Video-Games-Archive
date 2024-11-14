import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from games_archive.accounts.models import GamesArchiveUser
from games_archive.consoles.forms import ConsoleForm, ConsoleSearchForm
from games_archive.consoles.models import Console


class TestConsoleForm(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GamesArchiveUser.objects.create(
            username='testuser',
            email='user@email.com'
        )
        self.user.set_password('userpass')
        self.user.full_clean()
        self.user.save()

        # Setup test image path
        self.test_image_path = os.path.join(os.path.dirname(__file__), 'person.png')
        self.assertTrue(
            os.path.exists(self.test_image_path),
            f"Test image not found at {self.test_image_path}"
        )

    def test_console_form_valid_data_should_create_and_persists(self):
        self.client.force_login(self.user)

        # First, let's test the form directly
        with open(self.test_image_path, 'rb') as image_file:
            image_content = image_file.read()

        form_data = {
            'name': 'Test Console',
            'manufacturer': 'Test Manufacturer',
            'release_year': 2022,
            'description': 'This is a test console',
        }

        files_data = {
            'cover_image': SimpleUploadedFile(
                name='person.png',
                content=image_content,
                content_type='image/png'
            ),
            'logo': SimpleUploadedFile(
                name='person.png',
                content=image_content,
                content_type='image/png'
            )
        }

        # Test the form directly first
        form = ConsoleForm(data=form_data, files=files_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Now test the view
        response = self.client.post(
            reverse('console_create'),
            data={**form_data, **files_data},
            follow=True
        )

        # # Print response details for debugging
        # if response.context and 'form' in response.context:
        #     print(f"Form errors from response: {response.context['form'].errors}")
        # print(f"Response status code: {response.status_code}")
        # print(f"Response redirect chain: {response.redirect_chain}")

        # Check if console was created
        console = Console.objects.first()
        self.assertIsNotNone(console, "Console was not created")

        # Verify console details
        self.assertEqual(console.name, 'Test Console')
        self.assertEqual(console.manufacturer, 'Test Manufacturer')
        self.assertEqual(console.release_year, 2022)
        self.assertEqual(console.description, 'This is a test console')
        self.assertEqual(console.to_user, self.user)
        self.assertTrue(console.cover_image)
        self.assertTrue(console.logo)

    def test_console_form_invalid_data_should_raise(self):
        form = ConsoleForm(data={
            'name': 'T',
            'release_year': 'invalid',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('release_year', form.errors)

    def test_console_search_form(self):
        form = ConsoleSearchForm(data={'search': 'test'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search'], 'test')

        form = ConsoleSearchForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search'], '')