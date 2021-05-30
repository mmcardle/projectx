from unittest import mock

from projectx.users.admin import ProjectXUserAdmin, send_activation_email
from projectx.users.models import User


def test_send_activation_email(mocker):

    messages = mocker.patch("projectx.users.admin.messages")
    request = mock.Mock()
    user1 = mocker.Mock()
    user2 = mocker.Mock()
    queryset = [user1, user2]

    send_activation_email(None, request, queryset)

    assert messages.mock_calls == [
        mock.call.info(request, "%s Activation Email Sent." % user1),
        mock.call.info(request, "%s Activation Email Sent." % user2),
    ]
    assert user1.mock_calls == [mocker.call.send_account_activation_email(request)]
    assert user2.mock_calls == [mocker.call.send_account_activation_email(request)]


def test_admin():

    admin = ProjectXUserAdmin(User, mock.Mock())

    assert admin.readonly_fields == ("public_uuid", "modified", "created")
    assert admin.list_display == (
        "public_uuid",
        "email",
        "display_name",
        "is_active",
        "is_staff",
        "created",
        "modified",
    )
    assert admin.list_filter == ("is_active", "is_staff", "groups")
    assert admin.search_fields == ("email", "public_uuid")
    assert admin.ordering == ("email",)
