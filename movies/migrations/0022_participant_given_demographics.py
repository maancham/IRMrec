# Generated by Django 4.2.2 on 2023-07-31 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0021_participantinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='given_demographics',
            field=models.BooleanField(default=False),
        ),
    ]
