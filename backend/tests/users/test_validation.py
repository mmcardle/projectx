import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from marshmallow.exceptions import ValidationError

from common.validation import SchemaError, load_data_from_schema
from users import validation
from users.models import User


def test_numbervalidator():
    validation.NumberValidator(minimum=1).validate("1")


def test_uppercasevalidator():
    validation.UppercaseValidator(minimum=1).validate("A")


def test_lowercasevalidator():
    validation.LowercaseValidator(minimum=1).validate("a")


def test_symbolvalidator():
    validation.SymbolValidator(minimum=1).validate("$")


def test_numbervalidator_zero():
    validation.NumberValidator(minimum=0).validate("")


def test_uppercasevalidator_zero():
    validation.UppercaseValidator(minimum=0).validate("")


def test_lowercasevalidator_zero():
    validation.LowercaseValidator(minimum=0).validate("")


def test_symbolvalidator_zero():
    validation.SymbolValidator(minimum=0).validate("")


def test_numbervalidator_not_enough():
    with pytest.raises(DjangoValidationError):
        validation.NumberValidator(minimum=2).validate("1")


def test_uppercasevalidator_not_enough():
    with pytest.raises(DjangoValidationError):
        validation.UppercaseValidator(minimum=2).validate("A")


def test_lowercasevalidator_not_enough():
    with pytest.raises(DjangoValidationError):
        validation.LowercaseValidator(minimum=2).validate("a")


def test_symbolvalidator_not_enough():
    with pytest.raises(DjangoValidationError):
        validation.SymbolValidator(minimum=2).validate("$")


@pytest.mark.parametrize("symbol", validation.SymbolValidator.symbols)
def test_symbolvalidator_all_valid_chars(symbol):
    validation.SymbolValidator(minimum=1).validate(symbol)


def test_numbervalidator_help_text():
    assert validation.NumberValidator(minimum=1).get_help_text() == (
        "This password must contain at least 1 digit(s), 0-9."
    )
    assert validation.NumberValidator(minimum=2).get_help_text() == (
        "This password must contain at least 2 digit(s), 0-9."
    )


def test_uppercasevalidator_help_text():
    assert validation.UppercaseValidator(minimum=1).get_help_text() == (
        "This password must contain at least 1 uppercase letter, A-Z."
    )
    assert validation.UppercaseValidator(minimum=2).get_help_text() == (
        "This password must contain at least 2 uppercase letter, A-Z."
    )


def test_lowercasevalidator_help_text():
    assert validation.LowercaseValidator(minimum=1).get_help_text() == (
        "This password must contain at least 1 lowercase letter, a-z."
    )
    assert validation.LowercaseValidator(minimum=2).get_help_text() == (
        "This password must contain at least 2 lowercase letter, a-z."
    )


def test_symbolvalidator_help_text():
    assert validation.SymbolValidator(minimum=1).get_help_text() == (
        r"This password must contain at least 1 symbol: ()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
    )
    assert validation.SymbolValidator(minimum=2).get_help_text() == (
        r"This password must contain at least 2 symbol: ()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
    )


def make_valid_password():
    # make a password that passed alsl validaiton criteria
    return User.objects.make_random_password() + "aA$1"


def test_register_schema():
    data = {
        "email": "none@tempurl.com",
        "first_name": "first_name",
        "last_name": "last_name",
        "password1": "password",
        "password2": "password",
    }
    result = validation.RegisterSchema().load(data)
    assert result == data


def test_register_schema_non_matching_passwords():
    data = {
        "email": "none@tempurl.com",
        "first_name": "first_name",
        "last_name": "last_name",
        "password1": "Password_!1",
        "password2": "Password_!2",
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.RegisterSchema(), data)
    assert exception.value.errors == {"password2": ["Passwords must match."]}


def test_register_schema_bad_data():
    data = {
        "email": "not_an_email",
        "first_name": "X" * 50,
        "last_name": "X" * 50,
        "password1": "P1",
        "password2": "P2",
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.RegisterSchema(), data)
    assert exception.value.errors == {
        "email": ["Not a valid email address."],
        "first_name": ["First Name must be less than 40 characters."],
        "last_name": ["Last Name must be less than 40 characters."],
        "password1": ["Password must be greater than 8 characters."],
    }


def test_reset_check_schema_all_ok():
    data = {
        "reset_key": "reset_key",
    }
    result = validation.ResetPasswordCheckSchema().load(data)

    assert result == data


def test_reset_password_schema_all_ok():
    password = make_valid_password()
    data = {
        "reset_key": "reset_key",
        "password1": password,
        "password2": password,
    }
    result = validation.ResetPasswordCompleteSchema().load(data)

    assert result == data


def test_reset_password_load_data_from_schema_invalid():
    data = {
        "reset_key": "reset_key",
        "password1": "pass",
        "password2": "pass",
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.ResetPasswordCompleteSchema(), data)
    assert exception.value.errors["password1"] == [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common.",
        "This password must contain at least 1 digit(s), 0-9.",
        "This password must contain at least 1 uppercase letter, A-Z.",
        "This password must contain at least 1 symbol: ()[]{}|\\`~!@#$%^&*_-+=;:'\\\",<>./?",
    ]


def test_reset_password_complete_load_data_from_schema_passwords_dont_match():
    password1 = make_valid_password()
    password2 = make_valid_password()
    data = {
        "reset_key": "reset_key",
        "password1": password1,
        "password2": password2,
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.ResetPasswordCompleteSchema(), data)
    assert exception.value.errors["password2"] == ["Passwords must match."]


def test_change_password_schema():
    data = {
        "current_password": "current_password",
        "password1": "password",
        "password2": "password",
    }
    result = validation.ChangePasswordSchema().load(data)
    assert result == data


def test_change_password_non_matching_passwords():
    data = {
        "current_password": "current_password",
        "password1": "Password_!1",
        "password2": "Password_!2",
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.ChangePasswordSchema(), data)
    assert exception.value.errors == {"password2": ["Passwords must match."]}


def test_change_password_bad_data():
    data = {
        "current_password": "current_password",
        "password1": "P1",
        "password2": "P2",
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.ChangePasswordSchema(), data)
    assert exception.value.errors == {"password1": ["Password must be greater than 8 characters."]}


def test_change_details_schema():
    data = {
        "first_name": "first_name",
        "last_name": "last_name",
    }
    result = validation.ChangeDetailsSchema().load(data)
    assert result == data


def test_change_details_schema_bad_data():
    data = {
        "first_name": "X" * 50,
        "last_name": "X" * 50,
    }
    with pytest.raises(SchemaError) as exception:
        load_data_from_schema(validation.ChangeDetailsSchema(), data)
    assert exception.value.errors == {
        "first_name": ["First Name must be less than 40 characters."],
        "last_name": ["Last Name must be less than 40 characters."],
    }


@pytest.mark.django_db(transaction=True)
def test_activateschema_valid_key(mocker):

    user = User.objects.create(username="user")
    check_activation_key = mocker.patch("users.validation.User.check_activation_key", return_value=(user, None))

    schema = validation.ActivateSchema()
    result = schema.load({"activate_key": "activate_key"})

    assert result == {"activate_key": "activate_key", "user": user}

    assert check_activation_key.mock_calls == [mocker.call("activate_key")]


@pytest.mark.django_db(transaction=True)
def test_activateschema_bad_key(mocker):

    User.objects.create(username="user")
    check_activation_key = mocker.patch(
        "users.validation.User.check_activation_key", side_effect=[(None, None), (None, None)]
    )

    schema = validation.ActivateSchema()
    with pytest.raises(ValidationError) as exception:
        schema.load({"activate_key": "activate_key"})

    assert exception.value.messages["activate_key"] == ["Sorry that activation key is not valid."]
    assert check_activation_key.mock_calls == [mocker.call("activate_key"), mocker.call("activate_key", max_age=None)]


@pytest.mark.django_db(transaction=True)
def test_activateschema_expired_key(mocker):

    user = User.objects.create(username="user", email="user@example.com")
    check_activation_key = mocker.patch(
        "users.validation.User.check_activation_key", side_effect=[(None, None), (user, None)]
    )
    send_account_activation_email = mocker.patch("users.validation.User.send_account_activation_email")

    schema = validation.ActivateSchema()
    with pytest.raises(ValidationError) as exception:
        schema.load({"activate_key": "activate_key"})

    assert exception.value.messages["activate_key"] == [
        "That token has expired. A new email has been sent to your address. "
        "Please click on the new link in the email."
    ]
    assert check_activation_key.mock_calls == [mocker.call("activate_key"), mocker.call("activate_key", max_age=None)]
    assert send_account_activation_email.mock_calls == [mocker.call()]
