# Generated by Django 5.1.1 on 2024-10-29 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consoles', '0002_console_to_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('logo', models.ImageField(upload_to='suppliers_logos/')),
            ],
        ),
    ]