# Generated by Django 5.1.4 on 2025-01-13 20:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0016_studentanswer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='result',
            unique_together={('student', 'exam')},
        ),
    ]
