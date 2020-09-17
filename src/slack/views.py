import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import SlackEvent


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
    
    event = request_body.get('event')
    slack_event = SlackEvent(payload=request_body)
    slack_event.save()
    return JsonResponse({'ok': True})


def xapi_manager(request):
    """ UI configure xAPI statements """
    return render(request, 'statement_manager.html', {
        'events': {}
    })