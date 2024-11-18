import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Exports groups and permissions to a JSON file in the current directory'

    def handle(self, *args, **options):
        # Get the current directory where the command file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'groups_export.json')

        # Check if the file already exists
        if os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} already exists and will be overwritten.'))

        # Collect group data
        groups_data = []
        for group in Group.objects.all():
            permissions = list(group.permissions.values_list('codename', flat=True))
            groups_data.append({
                'name': group.name,
                'permissions': permissions,
            })

        # Write to the JSON file
        with open(file_path, 'w') as f:
            json.dump(groups_data, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Groups and permissions exported successfully to {file_path}'))

