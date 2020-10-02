# Create your tasks here
import json
import logging
import requests

from celery import shared_task
from xapi.models import LrsConfig

log = logging.getLogger(__name__)


@shared_task
def send_xapi_statement_to_lrs(xapi_statement):
    log.info(xapi_statement)
    lrs_configs = LrsConfig.objects.all()
    if not lrs_configs:
        log.exception("No LRS defined yet. Cannot send xAPI statment")
        return

    headers = {'Content-type': 'application/json;charset=UTF-8',
               'x-experience-api-version': '1.0.1'}

    res = requests.post(lrs_configs[0].lrs_endpoint,
                        data=json.dumps(xapi_statement, default=str),
                        auth=(lrs_configs[0].lrs_auth_user,
                              lrs_configs[0].lrs_auth_pw),
                        headers=headers)
    if res.status_code != 200:
        log.exception(res.content)
        return
    log.info("successfully sent statement")
    return
