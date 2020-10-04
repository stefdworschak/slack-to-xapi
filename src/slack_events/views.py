import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import RawSlackEvent, SlackEvent
from .tasks import schedule_xapi_task

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

    schedule_xapi_task.delay(request_body)
    return JsonResponse({'ok': True})


def statement_manager(request):
    """ UI configure xAPI statements """
    raw_slack_event = RawSlackEvent.objects.last()
    payload = dict(raw_slack_event.payload)
    slack_event = SlackEvent(_payload=json.dumps(payload))
    slack_event.save()

    return render(request, 'statement_manager.html', {
        'slack_event': slack_event,
    })
