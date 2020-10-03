import json

from django.test import TestCase

from xapi.models import (XApiActor, XApiVerb, XApiObject, SlackVerbField,
                         SlackObjectField)
from slack_events.models import SlackEvent
from django.contrib.auth.models import User

TEST_USERNAME = 'user@example.com'
TEST_USER_PASSWORD = 'fakepassword'


class XApiConversionUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=TEST_USERNAME,
                                        password=TEST_USER_PASSWORD)
        self.a1 = XApiActor.objects.create(
            iri='actor1@example.com',
            iri_type='mbox',
            display_name='Actor 1',
            slack_user_id='A123',
            object_type='Agent',
            created_by=self.user,
        )
        self.a2 = XApiActor.objects.create(
            iri='actor1@example.com',
            iri_type='mbox',
            display_name='Actor 2',
            slack_user_id='U123456',
            object_type='Agent',
            created_by=self.user,
        )
        self.a3 = XApiActor.objects.create(
            iri='slack_actor',
            iri_type='account',
            display_name='Actor 3',
            slack_user_id='U9876543',
            object_type='Agent',
            created_by=self.user,
        )
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
        self.xapi_object2 = XApiObject(
            created_by=self.user,
            iri='http://example.com/activities/reaction',
            display_name="Reaction",
            language="en-US",
            extensions=json.dumps(['event_id', 'message_text', 'team_id'])
        )
        self.xapi_object2.save()
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
        SlackObjectField.objects.create(
            created_by=self.user,
            slack_event_field='event_type',
            expected_value='reaction_added',
            xapi_object=self.xapi_object2
        )
        SlackObjectField.objects.create(
            created_by=self.user,
            slack_event_field='event_subtype',
            expected_value='message',
            xapi_object=self.xapi_object2
        )

    def test_slack_id_to_xapi_actor(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

        expected = {
            "actor": {
                "name": "Actor 2",
                "objectType": "Agent",
                "mbox": "mailto:actor1@example.com"
            }
        }

        xapi_actor = self.a2.slack_id_to_xapi_actor(slack_event)
        self.assertTrue(isinstance(xapi_actor, dict))
        self.assertEquals(xapi_actor, expected)

    def test_slack_id_to_xapi_actor_with_account(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

        expected = {
            "actor": {
                "name": "Actor 2",
                "objectType": "Agent",
                "account": {
                    "homePage": "http://slack.com",
                    "name": "slack_actor"
                }
            }
        }

        xapi_actor = self.a2.slack_id_to_xapi_actor(slack_event)
        self.assertTrue(isinstance(xapi_actor, dict))
        self.assertEquals(xapi_actor, expected)

    def test_slack_event_to_xapi_verb(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

        expected = {
                "verb": {
                    "id": "http://example.com/verbs/sent",
                    "display": {
                        "en-US": "sent"
                    }
                }
            }

        xapi_verb = XApiVerb.slack_event_to_xapi_verb(slack_event)
        self.assertTrue(isinstance(xapi_verb, dict))
        self.assertEquals(xapi_verb, expected)

    def test_model_to_xapi_object(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()

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
        self.assertEquals(self.xapi_object.model_to_xapi_object(slack_event),
                          expected)

    def test_model_to_xapi_object_with_extensions(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)

        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[1]))
        slack_event.save()

        expected = {
            "object": {
                "id": "http://example.com/activities/reaction",
                "definition": {
                    "name": {
                        "en-US": "Reaction"
                    },
                    "extensions": {
                        "http://example.com/extensions/event_id": "Ev01BMNX530V",  # noqa: E501
                        "http://example.com/extensions/message_text": "+1",
                        "http://example.com/extensions/team_id": "T01AV5ATPA8"
                    }
                },
                "objectType": "Activity",
            }
        }
        self.assertTrue(SlackEvent.objects.all())
        self.assertEquals(self.xapi_object2.model_to_xapi_object(slack_event),
                          expected)

    def test_slack_event_to_xapi_object(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[1]))
        slack_event.save()
        xapi_verb = XApiObject.slack_event_to_xapi_object(slack_event)
        self.assertTrue(isinstance(xapi_verb, dict))

    def test_slack_event_to_xapi_statement(self):
        with open('data/slack_event_tests.json') as file:
            slack_event_payloads = json.load(file)
        slack_event = SlackEvent(_payload=json.dumps(slack_event_payloads[0]))
        slack_event.save()
        print(slack_event.slack_event_to_xapi_statement())
        self.assertTrue(isinstance(slack_event.slack_event_to_xapi_statement(),
                                   dict))
