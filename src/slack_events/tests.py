import json

from django.test import TestCase

from xapi.models import (XApiActor, XApiVerb, XApiObject, SlackVerbField,
                         SlackObjectField)
from .models import SlackEvent, XApiStatement

from django.contrib.auth.models import User

TEST_USERNAME = 'user@example.com'
TEST_USER_PASSWORD = 'fakepassword'
REAL_USER_ID = 'U01AP783ZLK'


class SlackEventUnitTest(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.user = User.objects.create(username=TEST_USERNAME,
                                        password=TEST_USER_PASSWORD)
        self.actor = XApiActor(
            created_by=self.user,
            iri=TEST_USERNAME,
            display_name='User',
            iri_type='mbox',
            slack_user_id='U123456'
        )
        self.actor.save()
        self.verb = XApiVerb(
            created_by=self.user,
            iri='http://example.com/verbs/sent',
            display_name='sent',
            language='en-US'
        )
        self.verb.save()
        self.x_object = XApiObject(
            created_by=self.user,
            iri='http://example.com/activities/message',
            display_name='Chat Message',
            language='en-US'
        )
        self.x_object.save()

        SlackVerbField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='message',
            xapi_verb=self.verb,
            field_group='sent_message'
        )
        SlackObjectField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='message',
            xapi_object=self.x_object,
            field_group='sent_message'
        )

    def test_slack_event_to_xapi_statement(self):
        expected = {
            'actor': {
                'name': 'User',
                'objectType': 'Agent',
                'mbox': 'mailto:user@example.com',
            },
            'verb': {
                    'id': 'http://example.com/verbs/sent',
                    'display': {
                        'en-US': 'sent'
                    }
            },
            'object': {
                'id': 'http://example.com/activities/message',
                'definition': {
                    'name': {
                        'en-US': 'Chat Message'
                    },
                },
                'objectType': 'Activity'
            }
        }
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)

        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

        self.assertEquals(
            json.dumps(slack_event.slack_event_to_xapi_statement()),
            json.dumps(expected))
        xapi_statement = XApiStatement.objects.get(slack_event=slack_event)
        self.assertTrue(isinstance(xapi_statement, XApiStatement))

    def test_create_actor_from_slack(self):
        self.admin_user = User(username='admin',
                               password=TEST_USER_PASSWORD)
        self.admin_user.save()

        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
            slack_event_payloads[0]['event']['user'] = REAL_USER_ID

        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

        self.assertTrue(isinstance(slack_event.create_actor_from_slack(),
                                   XApiActor))
