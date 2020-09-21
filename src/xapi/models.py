import json

from django.db import models
from django.contrib.auth.models import User

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


class Activity(models.Model):
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
                                   choices=ACTIVITY_OBJECT_TYPES)
    class Meta:
        verbose_name_plural = 'Activities'


class Actor(models.Model):
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
    object_type = models.CharField(max_length=255, choices=ACTOR_OBJECT_TYPES)

    def __str__(self):
        #if self.display_name:
        #    return f'{self.display_name} (Slack: {self.slack_user_id})'
        return f'{self.iri} (Slack: {self.slack_user_id})'

    @staticmethod
    def slack_id_to_xapi_actor(slack_user_id):
        actor = Actor.objects.get(slack_user_id=slack_user_id)
        return {
            'actor': {
                actor.iri_type: actor.iri,
                'name': actor.display_name,
                'objectType': actor.object_type,
            }
        }

    
class Verb(models.Model):
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
        fields_for_verb = SlackField.objects.filter(verb=self)
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
        for verb in Verb.objects.all():
            verb_fields = verb.verb_fields_to_dict()
            event = slack_event.__dict__
            verb_set = set(verb_fields.items())
            
            # Removing JSON fields because they cannot be converted to a set
            del event['_payload']
            del event['mentioned_users']

            if verb_set.issubset(set(slack_event.__dict__.items())):
                return verb.model_to_xapi_verb()
        return


class SlackField(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    slack_event_field = models.CharField(max_length=255)
    expected_value = models.CharField(
        max_length=255, help_text=('Enter `None` if the expected value is '
                                   'supposed to be empty'))
    verb = models.ForeignKey(
        Verb, 
        related_name='slack_connector_fields',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'Connect {self.slack_event_field} as {self.expected_value}'
