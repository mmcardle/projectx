# pylint: disable=no-self-use
import logging
import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from marshmallow import Schema, ValidationError, fields, post_load, validates

from users.models import User

logger = logging.getLogger(__name__)


class NumberValidator:
    def __init__(self, minimum=0):
        self.min = minimum

    def validate(self, password, user=None):
        # pylint: disable=unused-argument
        if not len(re.findall(r"\d", password)) >= self.min:
            raise DjangoValidationError(
                _(f"This password must contain at least {self.min} digit(s), 0-9."),
                code="password_no_number",
            )

    def get_help_text(self):
        return _(f"This password must contain at least {self.min} digit(s), 0-9.")


class UppercaseValidator:
    def __init__(self, minimum=0):
        self.min = minimum

    def validate(self, password, user=None):
        # pylint: disable=unused-argument
        if not len(re.findall(r"[A-Z]", password)) >= self.min:
            raise DjangoValidationError(
                _(f"This password must contain at least {self.min} uppercase letter, A-Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _(f"This password must contain at least {self.min} uppercase letter, A-Z.")


class LowercaseValidator:
    def __init__(self, minimum=0):
        self.min = minimum

    def validate(self, password, user=None):
        # pylint: disable=unused-argument
        if not len(re.findall(r"[a-z]", password)) >= self.min:
            raise DjangoValidationError(
                _(f"This password must contain at least {self.min} lowercase letter, a-z."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _(f"This password must contain at least {self.min} lowercase letter, a-z.")


class SymbolValidator:

    symbols = r"()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"

    def __init__(self, minimum=0):
        self.min = minimum

    def validate(self, password, user=None):
        # pylint: disable=unused-argument
        if not len(re.findall(r"[()[\]{}|\\`~!@#$%^&*_\-+=;:'\",<>./?]", password)) >= self.min:
            raise DjangoValidationError(
                _(f"This password must contain at least {self.min} symbol: {self.symbols}"),
            )

    def get_help_text(self):
        return _(f"This password must contain at least {self.min} symbol: {self.symbols}")


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)

    @validates("first_name")
    def validate_first_name(self, value):
        if len(value) > 40:
            raise ValidationError("First Name must be less than 40 characters.")

    @validates("last_name")
    def validate_last_name(self, value):
        if len(value) > 40:
            raise ValidationError("Last Name must be less than 40 characters.")

    @validates("password1")
    def validate_password1(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be greater than 8 characters.")

    @post_load
    def check_passwords(self, data, **kwargs):
        # pylint: disable=unused-argument
        if data["password1"] != data["password2"]:
            raise ValidationError("Passwords must match.", "password2")
        return data


class ResetPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordCheckSchema(Schema):
    reset_key = fields.Str(required=True)


class ResetPasswordCompleteSchema(Schema):
    reset_key = fields.Str(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)

    @validates("password1")
    def validate_password1(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as django_ex:
            raise ValidationError(django_ex.messages, "password1") from django_ex

    @post_load
    def check_passwords(self, data, **kwargs):
        # pylint: disable=unused-argument
        if data["password1"] != data["password2"]:
            raise ValidationError("Passwords must match.", "password2")
        return data


class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)

    @validates("password1")
    def validate_password1(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be greater than 8 characters.")

    @post_load
    def check_passwords(self, data, **kwargs):
        # pylint: disable=unused-argument
        if data["password1"] != data["password2"]:
            raise ValidationError("Passwords must match.", "password2")
        return data


class ChangeDetailsSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    @validates("first_name")
    def validate_first_name(self, value):
        if len(value) > 40:
            raise ValidationError("First Name must be less than 40 characters.")

    @validates("last_name")
    def validate_last_name(self, value):
        if len(value) > 40:
            raise ValidationError("Last Name must be less than 40 characters.")


class ActivateSchema(Schema):

    activate_key = fields.Str(required=True)

    def check_activate_key(self, activate_key):

        user, _ = User.check_activation_key(activate_key)
        if user is None:
            # User has failed activation check
            # Check if the token has expired
            expired_user, _ = User.check_activation_key(activate_key, max_age=None)
            if expired_user:
                expired_user.send_account_activation_email()
                raise ValidationError(
                    "That token has expired. A new email has been sent "
                    "to your address. Please click on the new "
                    "link in the email.",
                    "activate_key",
                )

            raise ValidationError("Sorry that activation key is not valid.", "activate_key")

        return user

    @post_load
    def post_process(self, data, **kwargs):
        # pylint: disable=unused-argument
        activate_key = data["activate_key"]
        data["user"] = self.check_activate_key(activate_key)
        return data
