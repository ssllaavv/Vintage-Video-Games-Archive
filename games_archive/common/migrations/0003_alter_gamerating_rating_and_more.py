# Generated by Django 5.1.1 on 2024-10-24 09:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_alter_consolerating_rating_alter_gamerating_rating'),
        ('games', '0002_rename_screenshots_screenshot'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerating',
            name='rating',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True),
        ),
        migrations.AlterUniqueTogether(
            name='gamerating',
            unique_together={('from_user', 'to_game')},
        ),
    ]
