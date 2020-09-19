from django.urls import path
from .views import slack_api, statement_manager

urlpatterns = [
    path('slack_api/', slack_api, name="slack_api"),
    path('statement_manager/', statement_manager, name="statement_manager"),
]