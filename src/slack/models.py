import collections

from django.db import models
from jsonfield import JSONField


class SlackEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    payload = JSONField(
        null=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})
