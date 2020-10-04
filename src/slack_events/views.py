import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import RawSlackEvent, SlackEvent
from .tasks import send_xapi_statement_to_lrs

log = logging.getLogger(__name__)


@csrf_exempt
def slack_api(request):
    """ Slack Events API interface """
    if not request.body:
        return JsonResponse({'ok': False})
    request_body = json.loads(request.body)

    if request_body.get('type') == 'url_verification':
        return JsonResponse({'challenge': request_body.get('challenge')})

    if not request_body.get('event'):
        return JsonResponse({'ok': False})

    slack_event = SlackEvent(_payload=json.dumps(request_body))
    slack_event.save()

    xapi_statement = slack_event.slack_event_to_xapi_statement()
    if xapi_statement:
        send_xapi_statement_to_lrs.delay(xapi_statement, slack_event)
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


def statement_manager(request):
    """ UI configure xAPI statements """
    raw_slack_event = RawSlackEvent.objects.last()
    payload = dict(raw_slack_event.payload)
    slack_event = SlackEvent(_payload=json.dumps(payload))
    slack_event.save()

    return render(request, 'statement_manager.html', {
        'slack_event': slack_event,
    })