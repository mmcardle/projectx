import logging

from marshmallow import Schema, ValidationError, fields, post_load, validates

logger = logging.getLogger(__name__)


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password1 = fields.Str(required=True)
    password2 = fields.Str(required=True)

    @validates("first_name")
    def validate_first_name(self, value):
        if len(value) > 40:
            raise ValidationError(
                "First Name must be less than 40 characters."
            )

    @validates("last_name")
    def validate_last_name(self, value):
        if len(value) > 40:
            raise ValidationError(
                "Last Name must be less than 40 characters."
            )

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

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
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



class ChangeDetailsSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    @validates("first_name")
    def validate_first_name(self, value):
        if len(value) > 40:
            raise ValidationError(
                "First Name must be less than 40 characters."
            )

    @validates("last_name")
    def validate_last_name(self, value):
        if len(value) > 40:
            raise ValidationError(
                "Last Name must be less than 40 characters."
            )