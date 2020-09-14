from django.urls import path
from .views import slack_api

urlpatterns = [
    path('slack_api/', slack_api, name="slack_api"),
]