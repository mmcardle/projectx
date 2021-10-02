import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from projectx.common.fields import JSONDefaultField
from projectx.common.models import UUIDModel


class SimpleModel(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    config = JSONDefaultField(default=dict)

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


class SimpleUUIDModel(UUIDModel):

    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class BadJSONModelWithDefault(models.Model):

    data = models.JSONField(default=dict)

    def __str__(self):
        return str(self.data)


class BadJSONModelWithNoDefault(models.Model):

    data = models.JSONField()

    def __str__(self):
        return str(self.data)


class GoodJSONModel(models.Model):

    data = models.JSONField(default=lambda: {"key": "value"})

    def __str__(self):
        return str(self.data)


def validate_not_greater_than_1(value):
    if value > 1:
        raise ValidationError(
            "%(value)s is greater than 1",
            params={"value": value},
        )


class ModelWithValidation(models.Model):

    number = models.IntegerField(default=1, validators=[validate_not_greater_than_1])

    def __str__(self):
        return str(self.number)


class SimpleModelWithChoices(models.Model):
    class ChoiceType(models.TextChoices):
        CHOICE1 = "CHOICE1"
        CHOICE2 = "CHOICE2"
        CHOICE3 = "Choice3"

    choice = models.CharField("Type", max_length=30, choices=ChoiceType.choices)

    def __str__(self):
        return str(self.choice)


class SimpleModelWithDefaultFields(models.Model):

    hidden_field_with_default = models.CharField("Default", max_length=30, default="Default")
    request_field_with_default = models.CharField("Default", max_length=30, default="Default")
    request_field_with_no_default = models.CharField("Default", max_length=30)
    field_with_blank_true = models.CharField(max_length=250, null=False, blank=True)
    field_with_blank_true_and_default = models.CharField(
        max_length=250, blank=False, default="field_with_blank_true_and_default"
    )
    json_field_with_default = models.JSONField(default=lambda: dict({"k": "v"}))

    def __str__(self):
        return f"SimpleModelWithDefaultFields {self.id}"


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
