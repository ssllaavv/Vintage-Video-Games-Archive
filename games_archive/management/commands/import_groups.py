from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
import json
import os


class Command(BaseCommand):
    help = 'Imports groups and permissions from a JSON file in the current directory'

    def handle(self, *args, **options):
        # Get the current directory where the command file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'groups_export.json')

        # Check if the file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} not found. Please ensure the file exists.'))
            return

        # Load and import the group data
        with open(file_path, 'r') as f:
            groups_data = json.load(f)

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            permissions = Permission.objects.filter(codename__in=group_data['permissions'])
            group.permissions.set(permissions)

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_data["name"]}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated group: {group_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Groups and permissions imported successfully.'))
