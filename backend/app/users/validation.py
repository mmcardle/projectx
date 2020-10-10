import logging

from marshmallow import Schema, ValidationError, fields, post_load, validates

logger = logging.getLogger(__name__)


class ResetCheckSchema(Schema):
    reset_key = fields.Str(required=True)


class ResetPasswordSchema(Schema):
    reset_key = fields.Str(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)

    @validates("password1")
    def validate_password1(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Password must be greater than 8 characters."
            )

    @post_load
    def check_passwords(self, data, **kwargs):
        if data["password1"] != data["password2"]:
            raise ValidationError("Passwords must match.", "password2")
        return data