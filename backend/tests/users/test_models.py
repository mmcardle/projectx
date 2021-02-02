import json
from datetime import datetime
from unittest import mock

import pytest
from django.core.signing import BadSignature
from django.utils.timezone import make_aware

from users.models import REDIS_PASSWORD_RESET_KEY, User


def test_user_to_json(mocker):
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
