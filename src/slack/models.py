import collections
from datetime import datetime
import json
import re

from django.db import models
from jsonfield import JSONField
import pytz

from xapi.models import XApiActor, XApiVerb, XApiObject

TZ = pytz.timezone("Europe/Dublin") 

class RawSlackEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    payload = JSONField(
        null=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})


class SlackEvent(models.Model):
    team_id = models.CharField(max_length=25, null=True, blank=True)
    api_type = models.CharField(max_length=25, null=True, blank=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)
    event_subtype = models.CharField(max_length=255, null=True, blank=True)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_time = models.DateField(null=True, blank=True)
    message_text = models.TextField(null=True, blank=True)
    user = models.CharField(max_length=255, null=True, blank=True)
    channel = models.CharField(max_length=255, null=True, blank=True)
    channel_type = models.CharField(max_length=255, null=True, blank=True)
    attachments = JSONField(null=True, blank=True)
    ts = models.DateTimeField(null=True, blank=True)
    mentioned_users = JSONField(null=True, blank=True)
    has_mentions = models.BooleanField(default=False)

    _payload = JSONField(null=True, blank=True)

    def __str__(self):
        return f'@{self.user} {self.event_type} {(self.event_subtype or "")} at {self.event_time}'  # noqa: E501

    def save(self, *args, **kwargs):
        """ Custom save function to convert the payload to individual
        fields """
        data = json.loads(self._payload)
        event_content = data.get('event', {})

        self.team_id = data.get('team_id')
        self.api_type = data.get('type')
        self.event_id = data.get('event_id')
        self.event_time = self.from_unix_to_localtime(data.get('event_time'))
        self.user = event_content.get('user')

        self.event_type = event_content.get('type')
        self.event_subtype = event_content.get('subtype')
        self.message_text = event_content.get('text')
        self.channel = event_content.get('channel')
        self.channel_type = event_content.get('channel_type')
        self.attachments = event_content.get('attachments')
        self.ts = self.from_unix_to_localtime(
            timestamp=(event_content.get('ts') or event_content.get('event_ts')),
            tz=TZ)

        # If event has a message, then take these values
        if event_content.get('message'):
            msg_content = event_content.get('message')
            self.user = msg_content.get('user')
            self.message_text = msg_content.get('text')
            self.attachments = msg_content.get('attachments')
        if event_content.get('item'):
            item_content = event_content.get('item')
            self.message_text = event_content.get('reaction')
            self.event_subtype = item_content.get('type')
            self.channel = item_content.get('channel')

        #if self.check_mentions(self.message_text):
        #    pass
        self.mentioned_users = self.get_mentions_from_message(self.message_text)
        if self.mentioned_users:
            self.has_mentions = True
        super(SlackEvent, self).save(*args, **kwargs)

    def get_attachments(self):
        return json.loads(self.attachments)
    
    def get_mentioned_users(self):
        return json.loads(self.mentioned_users)
    
    def get_payload(self):
        return json.loads(self._payload)

    @staticmethod
    def from_unix_to_localtime(timestamp, tz=None):
        if (isinstance(timestamp, str)):
            timestamp = float(timestamp)
        utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        if not tz:
            return utc_dt
        return tz.normalize(utc_dt.astimezone(tz))

    @staticmethod
    def get_mentions_from_message(message_text):
        regex_pattern = r'[<][@]((?:[A-Z]|[0-9])*)[>]'
        return re.findall(regex_pattern, message_text)


    def slack_event_to_xapi_statement(self):
        xapi_statement = {}
        xapi_actor = XApiActor.slack_id_to_xapi_actor(self.user)
        xapi_statement.update(xapi_actor)
        xapi_verb = XApiVerb.slack_event_to_xapi_verb(self)
        xapi_statement.update(xapi_verb)
        xapi_object = XApiObject.slack_event_to_xapi_object(self)
        xapi_statement.update(xapi_object)
        return xapi_statement