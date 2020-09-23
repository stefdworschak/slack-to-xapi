import json
import os

from django.test import TestCase

from xapi.models import (XApiActor, XApiVerb, XApiObject, SlackVerbField,
                         SlackObjectField)
from slack.models import SlackEvent
from django.contrib.auth.models import User

TEST_USERNAME = 'user@example.com'
TEST_USER_PASSWORD = 'fakepassword'


class XApiConversionUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=TEST_USERNAME,
                                        password=TEST_USER_PASSWORD)
        self.xapi_verb = XApiVerb(
            created_by=self.user,
            iri='http://example.com/verbs/sent',
            display_name='sent',
            language='en-US'
        )
        self.xapi_verb.save()
        self.xapi_object = XApiObject(
            created_by=self.user,
            iri='http://example.com/activities/message',
            display_name="Message",
            language="en-US"
        )
        self.xapi_object.save()
        SlackVerbField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='message',
            xapi_verb=self.xapi_verb
        )
        SlackVerbField.objects.create(
            created_by=self.user,
            slack_event_field='event_subtype',
            expected_value='None',
            xapi_verb=self.xapi_verb
        )
        SlackObjectField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='message',
            xapi_object=self.xapi_object
        )
        
    def test_slack_id_to_xapi_actor(self):
        a1 = XApiActor.objects.create(
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
        xapi_verb = XApiVerb.slack_event_to_xapi_verb(slack_event)
        self.assertTrue(isinstance(xapi_verb, dict))

    def test_model_to_xapi_object(self):
        expected = {
            "object": {
                "id": "http://example.com/activities/message",
                "definition": {
                    "name": {
                        "en-US": "Message"
                    },
                },
                "objectType": "Activity"
            }
        }
        self.assertEquals(self.xapi_object.model_to_xapi_object(), expected)

    def test_slack_event_to_xapi_verb(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()
        xapi_object = XApiObject.slack_event_to_xapi_object(slack_event)
        self.assertTrue(isinstance(xapi_object, dict))