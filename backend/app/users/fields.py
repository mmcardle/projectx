from django.db import models


class LowercaseEmailField(models.EmailField):
    def to_python(self, value):
        value = super().to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value
