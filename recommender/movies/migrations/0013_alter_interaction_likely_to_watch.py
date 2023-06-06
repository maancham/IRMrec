# Generated by Django 4.1.7 on 2023-04-18 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0012_participant_judge_finished_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interaction',
            name='likely_to_watch',
            field=models.CharField(blank=True, choices=[('Awful/Horrible', ''), ('Disappointed', ''), ('Not Interested', ''), ('Interested', ''), ('Very Interested', '')], max_length=20, null=True),
        ),
    ]
