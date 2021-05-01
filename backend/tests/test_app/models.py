import uuid

from django.db import models


class TestModel(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    config = models.JSONField(default=dict)

    class Meta:
        pass

    def __str__(self):
        return str(self.name)
