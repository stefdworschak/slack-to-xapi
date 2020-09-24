import json

from django.db import models
from django.contrib.auth.models import User

from jsonfield import JSONField

ACTOR_IRI_TYPES = [
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
        #if self.display_name:
        #    return f'{self.display_name} (Slack: {self.slack_user_id})'
        return f'{self.iri} (Slack: {self.slack_user_id})'

    @staticmethod
    def slack_id_to_xapi_actor(slack_user_id):
        actor = XApiActor.objects.get(slack_user_id=slack_user_id)
        return {
            'actor': {
                actor.iri_type: actor.iri,
                'name': actor.display_name,
                'objectType': actor.object_type,
            }
        }

    class Meta:
        verbose_name = 'XApi Actor'
        verbose_name_plural = 'XApi Actors'

class XApiObject(models.Model):
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
    extensions = JSONField(null=True, blank=True)
    # TODO: Add interaction type

    def __str__(self):
        return f'{self.display_name} ({self.language})'
    
    def object_fields_to_dict(self):
        object_dict = {}
        fields_for_object = SlackObjectField.objects.filter(xapi_object=self)
        for field in fields_for_object:
            expected_value = field.expected_value
            if field.expected_value == 'None':
                expected_value = None
            object_dict[field.slack_event_field] = expected_value
        return object_dict
    
    def model_to_xapi_object(self):
        xapi_object =  {
                "object": {
                    "id": self.iri,
                    "definition": {
                        "name": {
                            self.language: self.display_name
                        }
                    },
                    "objectType": self.object_type
                }
            }
        if self.description:
            xapi_object['object']['description'] = {
                self.language: self.description
            }
        if self.activity_type:
            xapi_object['object']['definition']['type'] = self.activity_type
        if self.more_info:
            xapi_object['object']['definition']['moreInfo'] = self.more_info
        return xapi_object

    @staticmethod
    def slack_event_to_xapi_object(slack_event):
        for xobject in XApiObject.objects.all():
            object_fields = xobject.object_fields_to_dict()
            if not object_fields:
                continue
            event = slack_event.__dict__
            object_set = set(object_fields.items())
            # Removing JSON fields because they cannot be converted to a set
            if '_payload' in event:
                del event['_payload']
            if 'mentioned_users' in event:
                del event['mentioned_users']
            if object_set.issubset(set(slack_event.__dict__.items())):
                return xobject.model_to_xapi_object()
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
            expected_value = field.expected_value
            if field.expected_value == 'None':
                expected_value = None
            verb_dict[field.slack_event_field] = expected_value
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
            verb_fields = verb.verb_fields_to_dict()
            if not verb_fields:
                continue
            event = slack_event.__dict__
            verb_set = set(verb_fields.items())
            # Removing JSON fields because they cannot be converted to a set
            if '_payload' in event:
                del event['_payload']
            if 'mentioned_users' in event:
                del event['mentioned_users']
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

    def __str__(self):
        return f'Connect {self.slack_event_field} as {self.expected_value}'

    class Meta:
        verbose_name = 'Slack-Object Field'
        verbose_name_plural = 'Slack-Object Fields'