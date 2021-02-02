from unittest import mock

import pytest

from users.admin import ProjectXUserAdmin
from users.models import User


def test_admin(mocker):

    admin = ProjectXUserAdmin(User, mock.Mock())

    assert admin.readonly_fields == ("public_uuid", "modified", "created")
    assert admin.list_display == ("public_uuid", "email", "display_name",
                                  "is_active", "is_staff", "created", "modified")
    assert admin.list_filter == ("is_active", "is_staff", "groups")
    assert admin.search_fields == ("email", "public_uuid")
    assert admin.ordering == ("email",)
