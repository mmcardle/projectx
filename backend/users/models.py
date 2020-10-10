from django.db import models
from django.urls import reverse

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    # Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("users_User_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("users_User_update", args=(self.pk,))
