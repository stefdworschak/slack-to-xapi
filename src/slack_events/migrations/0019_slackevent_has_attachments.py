# Generated by Django 3.1.1 on 2020-10-10 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slack_events', '0018_auto_20201007_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackevent',
            name='has_attachments',
            field=models.BooleanField(default=False),
        ),
    ]