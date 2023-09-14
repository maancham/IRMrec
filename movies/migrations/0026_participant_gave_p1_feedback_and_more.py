# Generated by Django 4.2.2 on 2023-09-14 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0025_rename_rank_interaction_rank_p1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='gave_p1_feedback',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participant',
            name='gave_p2_feedback',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participant',
            name='p1_feedback',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='p2_feedback',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
