# Generated by Django 5.0.7 on 2024-08-01 19:44

import mandalarts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mandalarts', '0009_merge_20240801_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subgoal',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=mandalarts.models.mandalart_directory_path),
        ),
    ]