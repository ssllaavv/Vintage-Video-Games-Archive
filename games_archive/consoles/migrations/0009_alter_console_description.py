# Generated by Django 5.1.1 on 2024-11-07 12:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consoles', '0008_remove_console_unique_console_name_ci_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='console',
            name='description',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(1000)]),
        ),
    ]