# Generated by Django 4.1.7 on 2023-04-26 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0014_remove_participant_judge_finished_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='taken_initial_quiz',
            field=models.BooleanField(default=False),
        ),
    ]
