import json

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from jsonfield import JSONField

from main.helper import get_or_none

ACTOR_IRI_TYPES = [
    ('account', 'Account'),
    ('mbox', 'Email Address'),
    ('mbox_sha1sum', 'Email SHA1'),
    ('openid', 'OpenID'),
]

ACTOR_OBJECT_TYPES = [
    ('Agent', 'Agent'),
    ('Group', 'Group'),
]

ACTIVITY_OBJECT_TYPES = [
    ('Activity', 'Activity'),
    ('Agent', 'Agent'),
    ('Group', 'Group'),
    ('Statement Reference', 'Statement Reference'),
    ('SubStatement', 'SubStatement'),
]

ISO_LANGUAGE_CHOICES = [
    ('en-US', 'US English'),
    ('en-UK', 'UK English'),
    ('it', 'Italian'),
    ('es', 'Spanish'),
    ('de', 'German'),
]

SLACK_FIELD_TYPE_CHOICES = [
    ('verb', 'Verb'),
    ('object', 'Object'),
]

SLACK_URL = 'http://slack.com'

EXTENSIONS = {
    "team_id": "http://example.com/extensions/team_id",
    "api_type": "http://example.com/extensions/api_type",
    "event_type": "http://example.com/extensions/event_type",
    "event_subtype": "http://example.com/extensions/event_subtype",
    "event_id": "http://example.com/extensions/event_id",
    "event_time": "http://example.com/extensions/event_time",
    "message_text": "http://example.com/extensions/message_text",
    "user_id": "http://example.com/extensions/user_id",
    "channel": "http://example.com/extensions/channel",
    "channel_type": "http://example.com/extensions/channel_type",
    "attachments": "http://example.com/extensions/attachments",
    "ts": "http://example.com/extensions/ts",
    "mentioned_users": "http://example.com/extensions/mentioned_users",
    "has_mentions": "http://example.com/extensions/has_mentions",
}


class XApiActor(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    iri = models.CharField(
        max_length=1048,
        help_text=('Enter either email address, SHA1 of an email address or an'
                   'OpenID uri.'))
    iri_type = models.CharField(max_length=255, choices=ACTOR_IRI_TYPES)
    slack_user_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    object_type = models.CharField(max_length=255, choices=ACTOR_OBJECT_TYPES,
                                   default='Agent')

    def __str__(self):
        return f'{self.iri} (Slack: {self.slack_user_id})'

    @staticmethod
    def slack_id_to_xapi_actor(event):
        """ Converts the actor information from a Slack Event to an actor
        partial xAPI statement """
        prefix = ''
        actor = get_or_none(XApiActor, slack_user_id=event.user_id)
        if not actor:
            actor = event.create_actor_from_slack()

        actor_statement = {
            'actor': {
                'name': actor.display_name,
                'objectType': actor.object_type,
            }
        }

        if actor.iri_type == 'mbox':
            prefix = 'mailto:'

        if actor.iri_type == 'account':
            actor_statement['actor']['account'] = {
                'homePage': SLACK_URL,
                'name': actor.iri
            }
        else:
            actor_statement['actor'][actor.iri_type] = (prefix + actor.iri)

        return actor_statement

    class Meta:
        verbose_name = 'XApi Actor'
        verbose_name_plural = 'XApi Actors'


class XApiObject(models.Model):
    # TODO: Add interaction type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    iri = models.CharField(
        max_length=1048,
        help_text=('Enter the Activity IRI.'))
    display_name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=ISO_LANGUAGE_CHOICES)
    description = models.TextField(null=True, blank=True)
    activity_type = models.CharField(
        max_length=1048,
        help_text=('Enter an Activity Type IRI if applicable. '
                   'See some examples at '
                   'https://registry.tincanapi.com/#home/activityTypes'),
        null=True, blank=True)
    more_info = models.CharField(
        max_length=1048,
        help_text=('Enter an IRI for more info.'),
        null=True, blank=True)
    object_type = models.CharField(max_length=255,
                                   choices=ACTIVITY_OBJECT_TYPES,
                                   default='Activity')
    extensions = JSONField(null=True, blank=True,
                           help_text=('Needs to be a valid list with the '
                                      'Slack Event attributes to be added to '
                                      'the Extensions '
                                      '(e.g. ["message_text", "event_id"]. '
                                      'The available Extensions can be '
                                      'configured in xapi/models.py'))
    id_field = models.CharField(max_length=20, default='event_id')

    def __str__(self):
        return f'{self.display_name} ({self.language})'

    def model_to_xapi_object(self, event):
        _id = ''
        if not self.iri[-1] == '\/':
            self.iri = self.iri + '/'

        if self.id_field == 'file_ids':
            _id = f'{self.iri}{event.file_ids[0]}'
        else:
            _id = f'{self.iri}{getattr(event, self.id_field) or event.event_id}'

        if settings.ENABLE_PERMALINKS and self.id_field == 'permalink':
            if event.permalink:
                _id = event.permalink

        xapi_object = {
                "object": {
                    "id": _id,
                    "definition": {
                        "name": {
                            self.language: self.display_name
                        }
                    },
                    "objectType": self.object_type
                }
            }

        if self.description:
            xapi_object['object']['definition']['description'] = {
                self.language: self.description
            }
        if self.activity_type:
            xapi_object['object']['definition']['type'] = self.activity_type
        if self.more_info:
            xapi_object['object']['definition']['moreInfo'] = self.more_info

        extensions = self.extensions
        if extensions:
            if not isinstance(extensions, list):
                extensions = json.loads(extensions)
            xapi_object['object']['definition'].setdefault('extensions', {})
            for extension in extensions:
                extension_key = EXTENSIONS.get(extension)
                extension_value = getattr(event, extension)
                xapi_object['object']['definition']['extensions'][extension_key] = extension_value  # noqa: E501

        if settings.ENABLE_PERMALINKS and event.permalink:
            xapi_object['object']['definition'].setdefault('extensions', {})
            xapi_object['object']['definition']['extensions'][
                'http://example.com/extensions/permalink'] = event.permalink
        return xapi_object

    def object_fields_to_dict(self):
        object_dict = {}
        fields_for_object = SlackObjectField.objects.filter(xapi_object=self)

        for field in fields_for_object:
            object_dict.setdefault(field.field_group, {})
            expected_value = field.expected_value
            if field.expected_value == 'None':
                expected_value = None
            if (field.expected_value == 'True'
                    or field.expected_value == 'False'):
                expected_value = field.expected_value == 'True'
            object_dict[field.field_group][field.slack_event_field] = expected_value  # noqa: E501
        if not object_dict:
            return None
        return object_dict

    @staticmethod
    def slack_event_to_xapi_object(slack_event):
        for xobject in XApiObject.objects.all():
            object_fieldset = xobject.object_fields_to_dict()
            if not object_fieldset:
                continue
            event = slack_event.__dict__
            # Removing JSON fields because they cannot be converted to a set
            if '_payload' in event:
                del event['_payload']
            if 'mentioned_users' in event:
                del event['mentioned_users']
            if 'attachments' in event:
                del event['attachments']
            if 'file_ids' in event:
                del event['file_ids']
            for fields in object_fieldset.values():
                object_set = set(fields.items())
                if object_set.issubset(set(slack_event.__dict__.items())):
                    return xobject.model_to_xapi_object(slack_event)
        return

    class Meta:
        verbose_name = 'XApi Object'
        verbose_name_plural = 'XApi Objects'


class XApiVerb(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    iri = models.CharField(
        max_length=1048,
        help_text=('Enter either verb IRI'))
    display_name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=ISO_LANGUAGE_CHOICES)

    def __str__(self):
        return f'{self.display_name} ({self.language})'

    def verb_fields_to_dict(self):
        verb_dict = {}
        fields_for_verb = SlackVerbField.objects.filter(xapi_verb=self)
        for field in fields_for_verb:
            verb_dict.setdefault(field.field_group, {})
            expected_value = field.expected_value
            if field.expected_value == 'None':
                expected_value = None
            if (field.expected_value == 'True'
                    or field.expected_value == 'False'):
                expected_value = bool(field.expected_value)
            verb_dict[field.field_group][field.slack_event_field] = expected_value  # noqa: E501
        return verb_dict

    def model_to_xapi_verb(self):
        return {
                "verb": {
                    "id": self.iri,
                    "display": {
                        self.language: self.display_name
                    }
                }
            }

    @staticmethod
    def slack_event_to_xapi_verb(slack_event):
        for verb in XApiVerb.objects.all():
            verb_fieldset = verb.verb_fields_to_dict()
            if not verb_fieldset:
                continue
            event = slack_event.__dict__
            # Removing JSON fields because they cannot be converted to a set
            if '_payload' in event:
                del event['_payload']
            if 'mentioned_users' in event:
                del event['mentioned_users']
            if 'attachments' in event:
                del event['attachments']
            if 'file_ids' in event:
                del event['file_ids']
            for fields in verb_fieldset.values():
                verb_set = set(fields.items())
                if verb_set.issubset(set(slack_event.__dict__.items())):
                    return verb.model_to_xapi_verb()
        return

    class Meta:
        verbose_name = 'XApi Verb'
        verbose_name_plural = 'XApi Verbs'


class SlackField(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    slack_field_type = models.CharField(max_length=255,
                                        choices=SLACK_FIELD_TYPE_CHOICES)
    slack_event_field = models.CharField(max_length=255)
    expected_value = models.CharField(
        max_length=255, help_text=('Enter `None` if the expected value is '
                                   'supposed to be empty'))

    def __str__(self):
        return f'Connect {self.slack_event_field} as {self.expected_value}'


class SlackVerbField(SlackField):
    xapi_verb = models.ForeignKey(
        XApiVerb,
        related_name='slack_field_connector',
        on_delete=models.CASCADE)
    field_group = models.CharField(
        max_length=50,
        help_text=("Use this field to group together multiple "
                   "SlackVerbFields"),
        null=True, blank=True)

    def __str__(self):
        return f'Connect {self.slack_event_field} as {self.expected_value}'

    class Meta:
        verbose_name = 'Slack-Verb Field'
        verbose_name_plural = 'Slack-Verb Fields'


class SlackObjectField(SlackField):
    xapi_object = models.ForeignKey(
        XApiObject,
        related_name='slack_field_connector',
        on_delete=models.CASCADE)
    field_group = models.CharField(
        max_length=50,
        help_text=("Use this field to group together multiple "
                   "SlackObjectFields"),
        null=True, blank=True)

    def __str__(self):
        return f'Connect {self.slack_event_field} as {self.expected_value}'

    class Meta:
        verbose_name = 'Slack-Object Field'
        verbose_name_plural = 'Slack-Object Fields'


class LrsConfig(models.Model):
    display_name = models.CharField(max_length=255, unique=True, null=True,
                                    blank=True)
    lrs_endpoint = models.CharField(max_length=255)
    lrs_auth_user = models.CharField(max_length=255)
    lrs_auth_pw = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name
