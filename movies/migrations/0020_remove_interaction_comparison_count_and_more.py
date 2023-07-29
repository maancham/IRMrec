# Generated by Django 4.2.2 on 2023-07-29 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0019_participant_fully_done'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interaction',
            name='comparison_count',
        ),
        migrations.RemoveField(
            model_name='interaction',
            name='likely_to_watch',
        ),
        migrations.AddField(
            model_name='interaction',
            name='familiarity',
            field=models.CharField(blank=True, choices=[('Never', 'Never heard of it'), ('Familiar', 'Familiar with movie'), ('Very familiar', 'Very familiar (read reviews, seen trailers, etc.)'), ('Seen', 'Seen it')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='interaction',
            name='will_to_watch',
            field=models.CharField(blank=True, choices=[('Not interested', ''), ('Somewhat interested', ''), ('Interested', ''), ('Very interested', ''), ('Extremely interested', '')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='seen_status',
            field=models.BooleanField(default=False),
        ),
    ]
