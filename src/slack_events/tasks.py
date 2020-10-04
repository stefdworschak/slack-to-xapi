# Create your tasks here
import json
import logging
import requests

from celery import shared_task
from slack_events.models import SlackEvent, XApiStatement
from xapi.models import LrsConfig

log = logging.getLogger(__name__)


@shared_task
def schedule_xapi_task(payload):
    """ Handle Slack Events Subscription Payload to xAPI conversion and 
    delivery to one (or multiple) LRS """
    slack_event = SlackEvent(_payload=json.dumps(payload))
    slack_event.save()

    xapi_statement = slack_event.slack_event_to_xapi_statement()

    if not xapi_statement:
        log.exception("xAPI Statement could not be generated")
        return

    lrs_configs = LrsConfig.objects.all()
    if not lrs_configs:
        log.exception("No LRS defined yet. Cannot send xAPI statment")
        return

    for lrs_config in lrs_configs:
        send_xapi_statement_to_lrs(lrs_config, xapi_statement, slack_event)
    return


def send_xapi_statement_to_lrs(lrs_config, xapi_statement, slack_event):
    """ Sends an xAPI statement to an LRS """
    headers = {'Content-type': 'application/json;charset=UTF-8',
               'x-experience-api-version': '1.0.1'}
    res = requests.post(lrs_config.lrs_endpoint,
                        data=json.dumps(xapi_statement, default=str),
                        auth=(lrs_config.lrs_auth_user,
                              lrs_config.lrs_auth_pw),
                        headers=headers)
    if res.status_code != 200:
        log.exception(res.content)
        return
    xapi_statement = XApiStatement.objects.filter(slack_event=slack_event)
    if xapi_statement:
        xapi_statement.update(delivered=True)
    log.info("Successfully sent xAPI statement to LRS")
    return
