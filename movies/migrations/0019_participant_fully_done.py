# Generated by Django 4.2.2 on 2023-06-12 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0018_alter_movie_runtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='fully_done',
            field=models.BooleanField(default=False),
        ),
    ]
