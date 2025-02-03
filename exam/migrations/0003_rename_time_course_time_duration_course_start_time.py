# Generated by Django 5.1.4 on 2024-12-25 12:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_alter_question_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='time',
            new_name='time_duration',
        ),
        migrations.AddField(
            model_name='course',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
