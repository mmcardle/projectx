from django.db import models

EMPTY_VALUES = (None, "", [], ())


class JSONDefaultField(models.JSONField):
    empty_values = list(EMPTY_VALUES)
