import uuid

from django.contrib.auth import get_user_model
from django.db import models


class SimpleModel(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    config = models.JSONField(default=dict)

    def __str__(self):
        return str(self.name)


class SimpleJWTModel(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class UnauthenticatedModel(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class SimpleIDModel(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class SimpleModelWithOwner(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Question(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Choice(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")

    def __str__(self):
        return str(self.name)


class Topping(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Pizza(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return str(self.name)
