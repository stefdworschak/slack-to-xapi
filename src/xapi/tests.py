import json
import os

from django.test import TestCase

from xapi.models import Actor, Verb, SlackField
from slack.models import SlackEvent
from django.contrib.auth.models import User

TEST_USERNAME = 'user@example.com'
TEST_USER_PASSWORD = 'fakepassword'


class XApiConversionUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=TEST_USERNAME,
                                        password=TEST_USER_PASSWORD)
        self.verb = Verb(
            created_by=self.user,
            iri='http://example.com/verbs/sent',
            display_name='sent',
            language='en-US'
        )
        self.verb.save()
        SlackField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='message',
            verb=self.verb
        )
        SlackField.objects.create(
            created_by=self.user,
            slack_event_field='event_subtype',
            expected_value='None',
            verb=self.verb
        )
        
    def test_slack_id_to_xapi_actor(self):
        a1 = Actor.objects.create(
            iri='actor1@example.com',
            iri_type='mbox',
            display_name='Actor 1',
            slack_user_id='A123',
            object_type='Agent',
            created_by=self.user,
        )
        xapi_actor = a1.slack_id_to_xapi_actor(slack_user_id='A123')  
        self.assertTrue(isinstance(xapi_actor, dict))
    
    def test_slack_event_to_xapi_verb(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()
        xapi_verb = Verb.slack_event_to_xapi_verb(slack_event)
        self.assertTrue(isinstance(xapi_verb, dict))
    