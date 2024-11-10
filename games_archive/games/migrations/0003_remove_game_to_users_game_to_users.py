# Generated by Django 5.1.1 on 2024-10-24 11:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_rename_screenshots_screenshot'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='to_users',
        ),
        migrations.AddField(
            model_name='game',
            name='to_users',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
