# Generated by Django 5.1.4 on 2024-12-13 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Student', 'verbose_name_plural': 'students'},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='sex',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=4),
        ),
    ]
