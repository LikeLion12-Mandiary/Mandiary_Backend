# Generated by Django 4.2.14 on 2024-08-04 05:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mandalarts', '0012_rename_badge_dailybadge_user_badge_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailybadge',
            name='user_badge',
        ),
        migrations.AddField(
            model_name='dailybadge',
            name='badge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mandalarts.userbadge'),
        ),
        migrations.AlterUniqueTogether(
            name='goalachievement',
            unique_together={('user', 'achieved_goal')},
        ),
    ]
