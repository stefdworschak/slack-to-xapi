# Generated by Django 3.1.1 on 2020-09-21 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0002_auto_20200921_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xapiobject',
            name='object_type',
            field=models.CharField(choices=[('Activity', 'Activity'), ('Agent', 'Agent'), ('Group', 'Group'), ('Statement Reference', 'Statement Reference'), ('SubStatement', 'SubStatement')], default='Activity', max_length=255),
        ),
    ]
