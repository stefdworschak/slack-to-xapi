# Generated by Django 3.1.1 on 2020-09-16 20:19

import collections
from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SlackEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payload', jsonfield.fields.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True)),
            ],
        ),
    ]
