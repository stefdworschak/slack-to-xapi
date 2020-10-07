import collections
from datetime import datetime
import json
import logging
import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from jsonfield import JSONField
import pytz
from slack import WebClient

from xapi.models import XApiActor, XApiVerb, XApiObject
from xapi.models import ACTOR_IRI_TYPES
from main.helper import get_or_none, create_sha1

log = logging.getLogger(__name__)
TZ = pytz.timezone('Europe/Dublin')
SLACK_USER_API = ''
slack_client = WebClient(token=settings.SLACK_OAUTH_TOKEN)


class RawSlackEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    payload = JSONField(
        null=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    class Meta:
        verbose_name = "Raw Slack Event"
        verbose_name_plural = 'Raw Slack Events'


class SlackEvent(models.Model):
    team_id = models.CharField(max_length=25, null=True, blank=True)
    api_type = models.CharField(max_length=25, null=True, blank=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)
    event_subtype = models.CharField(max_length=255, null=True, blank=True)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_time = models.DateField(null=True, blank=True)
    message_text = models.TextField(null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    channel = models.CharField(max_length=255, null=True, blank=True)
    channel_type = models.CharField(max_length=255, null=True, blank=True)
    attachments = JSONField(null=True, blank=True)
    ts = models.DateTimeField(null=True, blank=True)
    mentioned_users = JSONField(null=True, blank=True)
    has_mentions = models.BooleanField(default=False)
    has_files = models.BooleanField(default=False)
    permalink = models.CharField(max_length=1048, null=True, blank=True)
    file_ids = JSONField(null=True, blank=True)

    _payload = JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Slack Event"
        verbose_name_plural = 'Slack Events'

    def __str__(self):
        return f'@{self.user_id} {self.event_type} {(self.event_subtype or "")} at {self.event_time}'  # noqa: E501

    def save(self, *args, **kwargs):
        """ Custom save function to convert the payload to individual
        fields """
        data = json.loads(self._payload)
        event_content = data.get('event', {})

        self.team_id = data.get('team_id')
        self.api_type = data.get('type')
        self.event_id = data.get('event_id')
        self.event_time = self.from_unix_to_localtime(data.get('event_time'))
        self.user_id = (event_content.get('user')
                        or event_content.get('user_id')
                        or data.get('authed_users')[0])

        self.event_type = event_content.get('type')
        self.event_subtype = event_content.get('subtype')
        self.message_text = event_content.get('text')
        self.channel = event_content.get('channel')
        self.channel_type = event_content.get('channel_type')
        self.attachments = event_content.get('attachments')
        message_ts = (event_content.get('ts')
                      or event_content.get('event_ts')
                      or event_content.get('item', {}).get('event_ts')
                      or event_content.get('message', {}).get('event_ts'))
        self.ts = self.from_unix_to_localtime(
            timestamp=message_ts, tz=TZ)

        # If event has a message, then take these values
        if event_content.get('message'):
            msg_content = event_content.get('message')
            self.user_id = msg_content.get('user')
            self.message_text = msg_content.get('text')
            self.attachments = msg_content.get('attachments')
        if event_content.get('item'):
            item_content = event_content.get('item')
            self.message_text = event_content.get('reaction')
            self.event_subtype = item_content.get('type')
            self.channel = item_content.get('channel')

        self.has_files = bool(
            event_content.get('files') or event_content.get('file') or
            event_content.get('attachment', {}).get('files') or
            event_content.get('item', {}).get('message', {}).get('items')
            or event_content.get('file_id'))

        if event_content.get('files'):
            log.info("Files: ", event_content.get('files'))
            self.file_ids = json.dumps(
                [shared_file.get('id')
                 for shared_file in event_content.get('files')])
        else:
            file_id = (event_content.get('file_id') or
                       event_content.get('file', {}).get('id'))
            log.info(f"File ID: {file_id}")
            self.file_ids = [file_id]

        # Need to check the item and message timestamp first in case it is a
        # reaction and if it does not exist use the normal ts
        # For the actual ts field it should be the reverse logic
        options = {
            'message_ts': (event_content.get('item', {}).get('event_ts')
                           or event_content.get('message', {}).get('event_ts')
                           or event_content.get('ts')
                           or event_content.get('event_ts'))
        }
        self.permalink = self.get_permalink_from_slack(options)
        self.mentioned_users = self.get_mentions_from_message(self.message_text)  # noqa: E501
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
        if not message_text or message_text == '':
            return None
        regex_pattern = r'[<][@]((?:[A-Z]|[0-9])*)[>]'
        return re.findall(regex_pattern, message_text)

    def slack_event_to_xapi_statement(self):
        xapi_statement = {}
        xapi_actor = XApiActor.slack_id_to_xapi_actor(self)
        # If actor is not found try yo create the actor automatically
        # if the setting is enabled
        if not xapi_actor:
            xapi_actor = self.create_actor_from_slack()
        # If no actor is found and a new one cannot be created return None
        if not xapi_actor:
            return None
        log.info("actor exsist")
        xapi_statement.update(xapi_actor)
        xapi_verb = XApiVerb.slack_event_to_xapi_verb(self)
        # If no matching verb was found return None
        if not xapi_verb:
            return None
        log.info("verb exsist")
        xapi_statement.update(xapi_verb)
        xapi_object = XApiObject.slack_event_to_xapi_object(self)
        # If no matching object was found return None
        if not xapi_object:
            return None
        log.info("object exsist")
        xapi_statement.update(xapi_object)
        statement = XApiStatement(
            statement=json.dumps(xapi_statement, default=str),
            slack_event=self)
        statement.save()
        return xapi_statement

    def create_actor_from_slack(self):
        """ Check if Actor exists and try to create it by looking up the info
        from their Slack profile if feature is enabled """
        if not settings.ACTOR_CREATION_ENABLED:
            log.warning("Automatic actor creation not enabled")
            return

        existing_actor = get_or_none(XApiActor, slack_user_id=self.user_id)
        if existing_actor:
            return existing_actor

        admin_user = get_or_none(User, username='admin')
        if not admin_user:
            log.warning("Admin user for automatic actor creation not found")
            return

        slack_call = slack_client.users_info(user=self.user_id)
        if not slack_call.get('ok'):
            return

        user_data = slack_call.get('user')
        email = user_data.get('profile', {}).get('email')
        if not email:
            log.warning("No email in Slack user found")
            return

        if settings.ACTOR_IRI_TYPE not in [t[0] for t in ACTOR_IRI_TYPES]:
            log.warning("Iri type declared is invalid")
            return

        if settings.ACTOR_IRI_TYPE == 'mbox_sha1sum':
            email = create_sha1(email)

        actor = XApiActor(
            created_by=admin_user,
            slack_user_id=self.user_id,
            iri=email,
            iri_type=settings.ACTOR_IRI_TYPE,
            display_name=(
                user_data.get('profile', {}).get('display_name')
                or user_data.get('real_name'))
        )
        actor.save()
        return get_or_none(XApiActor, slack_user_id=self.user_id)

    def get_permalink_from_slack(self, options):
        """ Gets the permalink for the message, file or conversation through
        the Slack API """
        log.info(f'Event Type: {self.event_type}')
        log.info(f'Channel: {self.channel}')
        message_ts = options.get('message_ts')
        log.info(f'Message TS: {message_ts}')
        if not settings.ENABLE_PERMALINKS:
            log.info("Permalinks are not enabled.")
            return None

        if self.permalink:
            log.info("Permalink already exists.")
            return self.permalink

        if 'deleted' in self.event_type:
            return
        elif (self.event_type == 'member_joined_channel' or
                self.event_type == 'member_left_channel'):
            if not self.channel:
                log.exception("No channel id found.")
                return

            team_info_call = slack_client.team_info(team=self.team_id)
            if not team_info_call.get('ok'):
                log.exception(team_info_call.get('error'))
                return

            domain = (team_info_call.get('team', {}).get('domain') or
                      team_info_call.get('team', {}).get('name'))
            return f'https://{domain}/archives/{self.channel}'
        elif (self.event_type != 'file_share' and 'file' in self.event_type
                and self.has_files):
            log.info('Getting permalink for file')
            if not self.file_ids:
                log.exception('No file ids found')
                return
            file_id = self.file_ids[0]
            file_info_call = slack_client.files_info(file=file_id)
            if not file_info_call.get('ok'):
                log.exception(file_info_call.get('error'))
                return
            return (file_info_call.get('file', {}).get('permalink')
                    or file_info_call.get('file', {}).get('url_private'))
        elif self.event_type == 'reaction_added':
            # TODO: use reactions.get with channel and ts (not event_ts)
            # response has a permalink element
            return
        elif self.event_type == 'star_added' or self.event_type == 'pin_added':
            # TODO: get the url_private or permalink from the message element
            # in the payload
            return
        else:
            return
            log.info('Getting permalink for message')
            if not self.channel or not (self.ts or self.event_ts):
                return
            permalink_call = slack_client.chat_getPermalink(
                channel=self.channel, message_ts=message_ts)
            if not permalink_call.get('ok'):
                log.exception(permalink_call.get('error'))
                return
            return permalink_call.get('permalink')


class XApiStatement(models.Model):
    statement = JSONField()
    delivered = models.BooleanField(default=False)
    slack_event = models.ForeignKey(SlackEvent, on_delete=models.CASCADE,
                                    related_name="slack_event")

    class Meta:
        verbose_name = "xAPI Statement"
        verbose_name_plural = 'xAPI Statements'

    def __str__(self):
        return f'{self.slack_event} (delivered: {self.delivered})'
