from django.urls import path
from .views import slack_xapi, statement_manager

urlpatterns = [
    path('slack/', slack_xapi, name="xapi_slack"),
    path('statement_manager/', statement_manager, name="statement_manager"),
]
