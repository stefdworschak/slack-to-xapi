from django.contrib import admin
from .models import RawSlackEvent, SlackEvent, XApiStatement


class XApiStatementAdmin(admin.ModelAdmin):
    model = XApiStatement
    list_display = ('slack_event', 'delivered',)
    list_filter = ('slack_event', 'delivered',)


admin.site.register(RawSlackEvent)
admin.site.register(SlackEvent)
admin.site.register(XApiStatement, XApiStatementAdmin)
