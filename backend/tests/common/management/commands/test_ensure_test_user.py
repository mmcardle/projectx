import pytest
from django.contrib.auth import get_user_model

from projectx.common.management.commands.ensure_test_user import (
    Command as EnsureTestUser,
)


def test_ensure_test_user_add_arguments(mocker):
    parser = mocker.Mock()
    command = EnsureTestUser()
    command.add_arguments(parser)
    assert parser.add_argument.mock_calls == [
        mocker.call("--email", help="Specifies the login."),
        mocker.call("--password", dest="password", default=None, help="Specifies the password."),
    ]


def test_ensure_test_user_no_password():
    command = EnsureTestUser()
    with pytest.raises(Exception):
        command.handle(email="test")


def test_ensure_test_user_no_email():
    command = EnsureTestUser()
    with pytest.raises(Exception):
        command.handle()


def test_ensure_test_user_existing(mocker):
    user_objects = mocker.patch("projectx.common.management.commands.ensure_test_user.User.objects")
    command = EnsureTestUser()
    command.handle(email="test@example.com", password="test_password")
    assert user_objects.mock_calls == [
        mocker.call.get(email="test@example.com"),
        mocker.call.get().set_password("test_password"),
        mocker.call.get().save(),
    ]


def test_ensure_test_user_non_existing(mocker):
    model = get_user_model()
    user_objects = mocker.patch(
        "projectx.common.management.commands.ensure_test_user.User.objects",
        get=mocker.Mock(side_effect=model.DoesNotExist),
    )
    command = EnsureTestUser()
    command.handle(email="test@example.com", password="test_password")
    assert user_objects.mock_calls == [
        mocker.call.get(email="test@example.com"),
        mocker.call.create_user("test@example.com", password="test_password"),
        mocker.call.create_user().save(),
    ]
