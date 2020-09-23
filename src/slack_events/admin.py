from django.contrib import admin
from .models import RawSlackEvent, SlackEvent


admin.site.register(RawSlackEvent)
admin.site.register(SlackEvent)
