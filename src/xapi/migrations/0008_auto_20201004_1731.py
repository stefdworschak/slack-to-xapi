# Generated by Django 3.1.1 on 2020-10-04 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0007_auto_20201003_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackobjectfield',
            name='connector_id',
            field=models.CharField(blank=True, help_text='Use this field to group together multipleSlackObjectFields', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='slackverbfield',
            name='connector_id',
            field=models.CharField(blank=True, help_text='Use this field to group together multipleSlackVerbFields', max_length=10, null=True),
        ),
    ]
