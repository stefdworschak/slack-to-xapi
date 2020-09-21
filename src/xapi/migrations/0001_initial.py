# Generated by Django 3.1.1 on 2020-09-19 18:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('iri', models.CharField(help_text='Enter either email address, SHA1 of an email address or anOpenID uri.', max_length=1048)),
                ('iri_type', models.CharField(choices=[('mbox', 'Email Address'), ('mbox_sha1sum', 'Email SHA1'), ('openid', 'OpenID')], max_length=255)),
                ('slack_user_id', models.CharField(max_length=255)),
                ('display_name', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
