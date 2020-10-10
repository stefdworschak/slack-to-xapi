# Generated by Django 3.1.1 on 2020-10-10 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0013_lrsconfig_display_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lrsconfig',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='lrsconfig',
            name='lrs_endpoint',
            field=models.CharField(max_length=255),
        ),
    ]
