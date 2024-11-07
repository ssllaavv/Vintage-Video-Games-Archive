# Generated by Django 5.1.1 on 2024-11-06 14:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_gamesarchiveuser_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesarchiveuser',
            name='age',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(120)]),
        ),
    ]
