# Generated by Django 3.1.1 on 2020-10-06 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slack_events', '0014_slackevent_has_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackevent',
            name='permalink',
            field=models.CharField(blank=True, max_length=1048, null=True),
        ),
    ]
