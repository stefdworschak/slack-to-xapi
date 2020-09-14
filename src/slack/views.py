import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def slack_api(request):
    request_body = json.loads(request.body)
    if request_body.get('type') == 'url_verification':
        return JsonResponse({'challenge': request_body.get('challenge')})
    print(request_body)
    return JsonResponse({'ok': True})