import uuid

from django.contrib.auth import get_user_model
from django.db import models


class TestModelWithOwner(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)
