# Generated by Django 5.1.4 on 2024-12-16 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'question', 'verbose_name_plural': 'questions'},
        ),
        migrations.RenameField(
            model_name='course',
            old_name='question_number',
            new_name='number_of_questions',
        ),
        migrations.AddField(
            model_name='course',
            name='time',
            field=models.IntegerField(help_text='duration of exam', null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='total_marks',
            field=models.PositiveIntegerField(default=None),
        ),
    ]
