import json
import logging
import requests
import time

from celery import shared_task
from slack_events.models import SlackEvent, XApiStatement
from xapi.models import LrsConfig

log = logging.getLogger(__name__)
RETRIES = 6
RETRY_INTERVAL = 10
TIMEOUT=3


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
    if not lrs_config.is_active:
        return

    headers = {'Content-type': 'application/json;charset=UTF-8',
               'x-experience-api-version': '1.0.1'}
    for retry in range(1, RETRIES+1):
        try:
            res = requests.post(lrs_config.lrs_endpoint,
                                data=json.dumps(xapi_statement, default=str),
                                auth=(lrs_config.lrs_auth_user,
                                      lrs_config.get_password()),
                                headers=headers,
                                timeout=TIMEOUT)
            if res.status_code == 200:
                break

            if retry == RETRIES:
                log.exception(f'Max retries exceeded. Reason: {res.reason}')
                return

        except requests.exceptions.ConnectionError as connection_error:
            if retry == RETRIES:
                log.exception(
                    f'Max retries exceeded. Reason: {str(connection_error)}')
                return

        log.exception(
            f'Error sending xAPI statement to {lrs_config.lrs_endpoint}. '
            f'{retry} out of {RETRIES} tries.')

    xapi_statement = XApiStatement.objects.filter(slack_event=slack_event)
    if xapi_statement:
        xapi_statement.update(delivered=True)
    log.info(f'Successfully sent xAPI statement to {lrs_config.lrs_endpoint}')
    return
