import uuid

from django.db import models


class TestModelWithJWT(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)
