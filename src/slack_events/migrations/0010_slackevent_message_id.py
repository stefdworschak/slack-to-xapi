# Generated by Django 3.1.1 on 2020-09-30 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slack_events', '0009_auto_20200923_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackevent',
            name='message_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
