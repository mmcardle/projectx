import json
from datetime import datetime
from unittest import mock

import pytest
from django.core.signing import BadSignature
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware

from users.models import (REDIS_ACCOUNT_ACTIVATION_KEY,
                          REDIS_PASSWORD_RESET_KEY, LowercaseEmailField, User)


@pytest.mark.django_db
def test_UserManager():

    user = User.objects.create_user("none@tempurl.com", password="pass")
    superuser = User.objects.create_superuser(email="super@tempurl.com", password="pass")
    user_with_username = User.objects.create_user("another@tempurl.com", password="pass", username="username")

    assert user.email == "none@tempurl.com"
    assert user.username == "none@tempurl.com"

    assert superuser.email == "super@tempurl.com"
    assert superuser.is_superuser

    assert user_with_username.email == "another@tempurl.com"
    assert user_with_username.username == "username"


def test_LowercaseEmailField():
    assert LowercaseEmailField().to_python(None) is None
    assert LowercaseEmailField().to_python("NONE@tempurl.com") == "none@tempurl.com"


@pytest.mark.django_db
def test_user_model_email_unique_case_insensitive():
    User.objects.create(email="none@tempurl.com")
    with pytest.raises(IntegrityError):
        User.objects.create(email="NONE@tempurl.com")


@pytest.mark.django_db
def test_user_model_create_inactive_user():
    data = {
        "email": "none@none.com",
        "password1": "password",
        "first_name": "first_name",
        "last_name": "last_name",
    }
    inactive_user = User.create_inactive_user(data)
    assert inactive_user.email == "none@none.com"
    assert inactive_user.first_name == "first_name"
    assert inactive_user.last_name == "last_name"


@pytest.mark.django_db
def test_user_model_email_exists_case_insensitive():
    User.objects.create(email="none@tempurl.com")
    assert User.email_exists("none@tempurl.com")
    assert User.email_exists("NONE@tempurl.com")


def test_user_model():
    user = User(
        public_uuid="bf113177-a583-41d9-8ad4-695114f4e30c",
        email="none@tempurl.com",
        first_name="First",
        last_name="Last"
    )
    assert user.to_json() == {
        "display_name": "First Last",
        "first_name": "First",
        "last_name": "Last",
        "email": "none@tempurl.com",
        "public_id": "bf113177-a583-41d9-8ad4-695114f4e30c",
        "role": "user",
        "last_login_timestamp": None,
        "last_login_timestamp_iso": None,
    }
    assert str(user) == "First Last"
    assert user.unique_name() == "none_tempurl_com_bf113177"
    assert user.last_login_timestamp() is None
    assert user.last_login_timestamp_iso() is None


def test_user_model_with_last_login():
    user = User(last_login=datetime(2000, 1, 1))
    assert user.last_login_timestamp() == 946684800
    assert user.last_login_timestamp_iso() == "2000-01-01T00:00:00"


def test_user_model_activate(mocker):
    user = User(is_active=False)
    user.save = mocker.Mock()
    user.activate()
    assert user.is_active
    assert user.save.mock_calls == [mocker.call()]


def test_user_send_reset_password_email(mocker):

    get_redis_connection = mocker.patch("users.models.get_redis_connection")
    settings = mocker.patch("users.models.settings")

    send_mail = mocker.patch("users.models.send_mail")
    signing = mocker.patch("users.models.signing")
    signing.dumps = mock.Mock(return_value="key")

    user = User(username="user", email="user@example.com")
    request = mocker.Mock()
    user.send_reset_password_email(request)
    expected_message = '''
Please click on the link below to reset your email within 24 hours ...
%s
Regards
ProjectX
''' % request.build_absolute_uri.return_value  # noqa

    assert send_mail.call_args[0][1] == expected_message
    assert send_mail.mock_calls == [
        mock.call(
            "Password Reset for user@example.com",
            mocker.ANY,  # Tested in assertion above for ease of debug
            settings.DEFAULT_FROM_EMAIL,
            ["user@example.com"]
        )
    ]

    assert get_redis_connection.return_value.hset.mock_calls == [
        mock.call(REDIS_PASSWORD_RESET_KEY, "user@example.com", b'{"key": "key"}')
    ]


def test_user_send_data_to_user(mocker):
    AsyncToSync = mocker.patch("users.models.AsyncToSync")
    get_channel_layer = mocker.patch("users.models.get_channel_layer")
    user = User(email="user1@tempurl.com", public_uuid="123456789")

    user.send_data_to_user({"data": "message"})

    assert AsyncToSync.mock_calls == [
        mock.call(get_channel_layer().group_send),
        mock.call()("user1_tempurl_com_12345678", {"type": "user.message", "data": '{"data": "message"}'})
    ]


def test_user_delete_reset_key(mocker):
    get_redis_connection = mocker.patch("users.models.get_redis_connection")
    User.delete_reset_key("key")

    assert get_redis_connection.return_value.mock_calls == [
        mock.call.hdel(REDIS_PASSWORD_RESET_KEY, "key")
    ]


def test_user_check_reset_key(mocker):

    redis_payload = json.dumps({"key": "key"})
    get_redis_connection = mocker.patch(
        "users.models.get_redis_connection",
        return_value=mock.Mock(hget=mock.Mock(return_value=redis_payload))
    )
    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        return_value={"email": "user@example.com"}
    )
    user = mock.Mock()
    mocker.patch.object(
        User, "objects",
        mock.Mock(get=lambda email__iexact: user)
    )
    check_user, error = User.check_reset_key("key")

    assert check_user == user
    assert error == ""
    assert get_redis_connection.return_value.hget.mock_calls == [
        mock.call(REDIS_PASSWORD_RESET_KEY, "user@example.com")
    ]


def test_user_check_reset_key_bad_signature(mocker):
    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        side_effect=BadSignature()
    )
    check_user, error = User.check_reset_key("key")

    assert check_user is None
    assert error == "Bad Signature"


def test_user_check_reset_key_doesnot_exist(mocker):
    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        return_value={"email": "user@example.com"}
    )
    mocker.patch.object(
        User, "objects",
        get=mock.Mock(side_effect=User.DoesNotExist())
    )
    check_user, error = User.check_reset_key("key")

    assert User.objects.get.mock_calls == [mock.call(email__iexact="user@example.com")]
    assert check_user is None
    assert error == "No such user"


def test_user_check_reset_key_payload_not_in_redis(mocker):

    get_redis_connection = mocker.patch(
        "users.models.get_redis_connection",
        return_value=mock.Mock(hget=mock.Mock(return_value=None))
    )

    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        return_value={"email": "user@example.com"}
    )

    user = mock.Mock()
    mocker.patch.object(User, "objects", mock.Mock(get=lambda email__iexact: user))
    check_user, error = User.check_reset_key("key")

    assert check_user is None
    assert error == "No Key found"
    assert get_redis_connection.return_value.hget.mock_calls == [
        mock.call(REDIS_PASSWORD_RESET_KEY, "user@example.com")
    ]


def test_user_check_reset_key_wrong_key_in_redis(mocker):

    redis_payload = json.dumps({"key": "WRONG_KEY"})
    get_redis_connection = mocker.patch(
        "users.models.get_redis_connection",
        return_value=mock.Mock(hget=mock.Mock(return_value=redis_payload))
    )

    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        return_value={"email": "user@example.com"}
    )

    user = mock.Mock()
    mocker.patch.object(User, "objects", mock.Mock(get=lambda email__iexact: user))
    check_user, error = User.check_reset_key("key")

    assert check_user is None
    assert error == "Key invalid or expired"
    assert get_redis_connection.return_value.hget.mock_calls == [
        mock.call(REDIS_PASSWORD_RESET_KEY, "user@example.com")
    ]


def test_user_check_activation_key(mocker):

    redis_payload = json.dumps({"key": "key"})
    get_redis_connection = mocker.patch(
        "users.models.get_redis_connection",
        return_value=mock.Mock(hget=mock.Mock(return_value=redis_payload))
    )
    signing = mocker.patch("users.models.signing")
    signing.loads = mock.Mock(
        return_value={"email": "user@example.com"}
    )
    user = mock.Mock()
    mocker.patch.object(
        User, "objects",
        mock.Mock(get=lambda email__iexact: user)
    )
    check_user, error = User.check_activation_key("key")

    assert check_user == user
    assert error == ""
    assert get_redis_connection.return_value.hget.mock_calls == [
        mock.call(REDIS_ACCOUNT_ACTIVATION_KEY, "user@example.com")
    ]


@pytest.mark.django_db
def test_user_reset_email(mocker):

    email = "none@tempurl.com"
    User.objects.create(username="user1", email=email)
    send_reset_password_email = mocker.patch.object(User, "send_reset_password_email")
    request = mocker.Mock()

    User.reset_email(email, request)

    assert send_reset_password_email.mock_calls == [mock.call(request)]


@pytest.mark.django_db
def test_user_reset_email_no_such_user(mocker):

    send_reset_password_email = mocker.patch.object(User, "send_reset_password_email")

    User.reset_email("ANOTHER@tempurl.com", mocker.Mock())

    assert send_reset_password_email.mock_calls == []


@pytest.mark.django_db
def test_user_send_account_activation_email(mocker):

    get_redis_connection = mocker.patch("users.models.get_redis_connection")
    settings = mocker.patch("users.models.settings")

    send_mail = mocker.patch("users.models.send_mail")
    signing = mocker.patch("users.models.signing")
    signing.dumps = mock.Mock(return_value="key")

    user = User.objects.create(username="user", email="user@example.com")
    request = mock.Mock()
    user.send_account_activation_email(request)
    expected_message = '''
Please click on the link below to activate your account within 24 hours ...
%s
Regards
ProjectX
''' % request.build_absolute_uri.return_value  # noqa
    assert send_mail.call_args[0][1] == expected_message
    assert send_mail.mock_calls == [
        mock.call(
            "Account Activation for user@example.com",
            mocker.ANY,  # Tested in assertion above for ease of debug
            settings.DEFAULT_FROM_EMAIL,
            ["user@example.com"]
        )
    ]

    assert get_redis_connection.return_value.hset.mock_calls == [
        mock.call(REDIS_ACCOUNT_ACTIVATION_KEY, "user@example.com", b'{"key": "key"}')
    ]
