# Generated by Django 3.1.1 on 2020-10-04 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slack_events', '0012_xapistatement'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rawslackevent',
            options={'verbose_name': 'Raw Slack Event', 'verbose_name_plural': 'Raw Slack Events'},
        ),
        migrations.AlterModelOptions(
            name='slackevent',
            options={'verbose_name': 'Slack Event', 'verbose_name_plural': 'Slack Events'},
        ),
        migrations.AlterModelOptions(
            name='xapistatement',
            options={'verbose_name': 'xAPI Statement', 'verbose_name_plural': 'xAPI Statements'},
        ),
    ]
