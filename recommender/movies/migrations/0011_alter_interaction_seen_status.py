# Generated by Django 4.1.7 on 2023-04-11 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0010_remove_interaction_has_seen_interaction_seen_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interaction',
            name='seen_status',
            field=models.CharField(blank=True, choices=[('Never', 'Never heard of it'), ('Heard', 'Just heard about it'), ('Seen', 'I have seen it')], max_length=20, null=True),
        ),
    ]
