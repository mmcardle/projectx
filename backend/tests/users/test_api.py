# pylint: disable=invalid-name disable=protected-access
import json
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django_ratelimit.exceptions import Ratelimited

from projectx.users import api


def make_request(**kwargs):
    if "META" not in kwargs:
        kwargs["META"] = {}

    if "REMOTE_ADDR" not in kwargs["META"]:
        # In order to not get hit by rate limits during tests we
        # have to make each request unique by adding a counter
        kwargs["META"]["REMOTE_ADDR"] = "127.0.0.1"

    if "session" not in kwargs:
        kwargs["session"] = mock.MagicMock(get=mock.Mock(return_value=[]))

    return mock.Mock(spec=HttpRequest, **kwargs)


def test_new_jwt_token(mocker):
    user = mocker.Mock(username="user")
    jwt_token = api.new_jwt_token(user)
    prefix = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    assert jwt_token.startswith(prefix)


def test_jwt_token_for_session_creates_new_jwt_token(mocker):
    new_jwt_token = mocker.patch("projectx.users.api.new_jwt_token")

    session = {}
    user = mocker.Mock(username="user")
    request = make_request(user=user, session=session)

    api.jwt_token_for_session(request)

    assert session == {api.JWT_SESSION_KEY: new_jwt_token.return_value}

    assert new_jwt_token.mock_calls == [mocker.call(user)]


def test_jwt_token_for_session_keeps_existing_jwt_token(mocker):
    new_jwt_token = mocker.patch("projectx.users.api.new_jwt_token")

    session = {api.JWT_SESSION_KEY: "Existing"}
    user = mocker.Mock(username="user")
    request = make_request(user=user, session=session)

    api.jwt_token_for_session(request)

    assert session == {api.JWT_SESSION_KEY: "Existing"}

    assert new_jwt_token.mock_calls == []


def test_request_is_sudo():
    assert api._request_is_sudo(make_request(session=mock.Mock(get=mock.Mock(return_value=[1]))))
    assert not api._request_is_sudo(make_request())


def test_get_logout_url_normal_request():
    assert api._get_logout_url(make_request()) == "/app/users/logout/"


def test_get_logout_url_su_request():
    su_request = make_request(session=mock.Mock(get=mock.Mock(return_value=[1])))
    assert api._get_logout_url(su_request) == "/admin/su/logout/"


def test_user_details_authenticated(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    mocker.patch("projectx.users.api._get_token", return_value="token")
    mocker.patch("projectx.users.api.jwt_token_for_session", return_value="jwt")

    user = mock.Mock()
    request = make_request(user=user)
    api.user_details(request)

    assert JsonResponse.mock_calls == [
        mock.call({"user": user.to_json(), "token": "token", "jwt": "jwt", "logout_url": "/app/users/logout/"})
    ]


def test_user_details_unauthenticated(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    user = mock.Mock(is_authenticated=False)
    request = make_request(user=user)
    api.user_details(request)

    assert JsonResponse.mock_calls == [mock.call({"user": None})]


def test_login_GET(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    mocker.patch("projectx.users.api._get_token", return_value="token")

    user = mock.Mock(is_authenticated=False)
    request = make_request(method="GET", user=user, META={"CSRF_COOKIE": "token"})
    api.login(request)
    assert JsonResponse.mock_calls[0] == mock.call({"token": "token"})


def test_login_POST_rate_limited(settings, mocker):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

    mocker.patch("projectx.users.api.JsonResponse")
    mocker.patch("projectx.users.api.authenticate")
    mocker.patch("projectx.users.api.django_login")
    mocker.patch("projectx.users.api.new_jwt_token")

    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST",
        user=user,
        body="{}",
        META={"CSRF_COOKIE": "token", "REMOTE_ADDR": "127.0.0.1"},
        session=mock.MagicMock(),
    )
    with pytest.raises(Ratelimited) as rate_limit_ex:
        for _ in range(0, 6):
            api.login(request)

    assert str(rate_limit_ex.value) == ""


def test_login_GET_no_csrf(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    user = mock.Mock(is_authenticated=False)
    request = make_request(method="GET", user=user)
    api.login(request)
    assert JsonResponse.mock_calls[0] == mock.call({"token": mock.ANY})


def test_login_POST(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    authenticate = mocker.patch("projectx.users.api.authenticate")
    django_login = mocker.patch("projectx.users.api.django_login")
    mocker.patch("projectx.users.api.new_jwt_token", return_value="jwt")

    body = json.dumps({"email": "email@none.com", "password": "password"})
    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST",
        user=user,
        body=body,
        META={"CSRF_COOKIE": "token"},
    )
    api.login(request)

    assert authenticate.call_args_list == [
        mock.call(request, username="email@none.com", password="password"),
    ]
    assert JsonResponse.call_args_list[0:1] == [
        mock.call(
            {
                "success": True,
                "user": authenticate().to_json(),
                "jwt": "jwt",
                "token": mock.ANY,
                "logout_url": "/app/users/logout/",
            }
        )
    ]
    assert django_login.mock_calls == [mock.call(request, authenticate())]


def test_login_POST_bad_auth_with_no_user(mocker):
    UserModel = get_user_model()

    mocker.patch.object(UserModel._default_manager, "get_by_natural_key", mock.Mock(side_effect=UserModel.DoesNotExist))
    mocker.patch.object(UserModel.objects, "get", mock.Mock(side_effect=UserModel.DoesNotExist))

    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    authenticate = mocker.patch("projectx.users.api.authenticate")
    authenticate.return_value = None
    django_login = mocker.patch("projectx.users.api.django_login")

    body = json.dumps({"email": "email@none.com", "password": "password"})
    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST",
        user=user,
        body=body,
        META={"CSRF_COOKIE": "token"},
    )
    api.login(request)
    assert JsonResponse.mock_calls[0:1] == [
        mock.call(
            {
                "success": False,
            },
            status=401,
        )
    ]
    assert authenticate.mock_calls == [mock.call(request, username="email@none.com", password="password")]
    assert django_login.mock_calls == []


def test_anonymous_POST(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    create_anonymous_user = mocker.patch("projectx.users.models.User.objects.create_anonymous_user")
    django_login = mocker.patch("projectx.users.api.django_login")
    mocker.patch("projectx.users.api.new_jwt_token", return_value="jwt")

    body = json.dumps({"email": "email@none.com", "password": "password"})
    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST",
        user=user,
        body=body,
        META={"CSRF_COOKIE": "token"},
    )
    api.anonymous(request)

    assert create_anonymous_user.call_args_list == [
        mock.call(),
    ]
    assert JsonResponse.call_args_list[0:1] == [
        mock.call(
            {
                "success": True,
                "user": create_anonymous_user().to_json(),
                "jwt": "jwt",
                "token": mock.ANY,
                "logout_url": "/app/users/logout/",
            }
        )
    ]
    assert django_login.mock_calls == [mock.call(request, create_anonymous_user())]


def test_logout(mocker):
    django_logout = mocker.patch("projectx.users.api.django_logout")
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    user = mock.Mock(is_authenticated=True)
    request = make_request(method="GET", user=user, path="http://127.0.0.1/path")
    api.logout(request)
    assert JsonResponse.mock_calls == [mock.call({"success": True})]
    assert django_logout.mock_calls == [mock.call(request)]


def test_logout_deletes_jwt(mocker):
    django_logout = mocker.patch("projectx.users.api.django_logout")
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    user = mock.Mock(is_authenticated=True)
    session = {api.JWT_SESSION_KEY: "token"}
    request = make_request(method="GET", user=user, path="http://127.0.0.1/path", session=session)
    api.logout(request)
    assert JsonResponse.mock_calls == [mock.call({"success": True})]
    assert django_logout.mock_calls == [mock.call(request)]
    assert not session


def test_register(mocker):
    User = mocker.patch(
        "projectx.users.api.models.User",
        email_exists=mocker.Mock(return_value=False),
    )
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    data = {
        "password2": "password",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email@tempurl.com",
        "password1": "password",
    }
    request = make_request(method="POST", body=json.dumps(data), user=mock.Mock())

    api.register(request)
    assert JsonResponse.mock_calls == [mock.call(User.create_inactive_user.return_value.to_json.return_value)]
    assert User.mock_calls == [
        mock.call.email_exists("email@tempurl.com"),
        mock.call.create_inactive_user(data),
        mock.call.create_inactive_user().send_account_activation_email(request),
        mock.call.create_inactive_user().to_json(),
    ]


def test_register_email_exists(mocker):
    User = mocker.patch(
        "projectx.users.api.models.User",
        email_exists=mocker.Mock(return_value=True),
    )
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    data = {
        "password2": "password",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email@tempurl.com",
        "password1": "password",
    }
    request = make_request(method="POST", body=json.dumps(data), user=mock.Mock())

    api.register(request)
    assert JsonResponse.mock_calls == [
        mock.call({"error": True, "errors": {"email": ["This email is already registered"]}}, status=401)
    ]
    assert User.mock_calls == [
        mock.call.email_exists("email@tempurl.com"),
    ]


def test_reset_password(mocker):
    User = mocker.patch(
        "projectx.users.api.models.User",
        email_exists=mocker.Mock(return_value=True),
    )
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"email": "none@example.com"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password(request)
    assert JsonResponse.mock_calls == [mock.call({})]
    assert User.mock_calls == [
        mock.call.email_exists("none@example.com"),
        mock.call.reset_email("none@example.com", request),
    ]


def test_reset_password_no_such_email(mocker):
    User = mocker.patch(
        "projectx.users.api.models.User",
        email_exists=mocker.Mock(return_value=False),
    )
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"email": "nosuchemail@example.com"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password(request)
    assert JsonResponse.mock_calls == [mock.call({})]
    assert User.mock_calls == [
        mock.call.email_exists("nosuchemail@example.com"),
    ]


def test_reset_password_check(mocker):
    user = mock.Mock()
    User = mocker.patch("projectx.users.api.models.User", check_reset_key=mock.Mock(return_value=(user, None)))
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"reset_key": "reset_key"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_check(request)
    assert JsonResponse.mock_calls == [mock.call({"email": user.email})]
    assert User.mock_calls == [
        mock.call.check_reset_key("reset_key"),
    ]


def test_reset_password_check_user_is_None(mocker):
    User = mocker.patch("projectx.users.api.models.User", check_reset_key=mock.Mock(return_value=(None, "error")))
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"reset_key": "reset_key"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_check(request)
    assert JsonResponse.mock_calls == [mock.call({"error": "error"}, status=401)]
    assert User.mock_calls == [
        mock.call.check_reset_key("reset_key"),
    ]


def test_reset_password_complete(mocker):
    user = mock.Mock()
    User = mock.Mock(check_reset_key=lambda key: (user, None))
    user_models = mocker.patch("projectx.users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"reset_key": "reset_key", "password1": "password_value_1A!", "password2": "password_value_1A!"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_complete(request)
    assert JsonResponse.mock_calls == [mock.call(user.to_json.return_value)]

    assert user.mock_calls == [
        mock.call.set_password("password_value_1A!"),
        mock.call.save(),
        mock.call.delete_reset_key(user.email),
        mock.call.to_json(),
    ]


def test_reset_password_complete_no_user(mocker):
    User = mock.Mock(check_reset_key=lambda key: (None, "error"))
    user_models = mocker.patch("projectx.users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"reset_key": "reset_key", "password1": "password_value_1A!", "password2": "password_value_1A!"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_complete(request)
    assert JsonResponse.mock_calls == [mock.call({"error": "error"}, status=401)]


def test_change_password(mocker):
    authenticate = mocker.patch("projectx.users.api.authenticate")
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    update_session_auth_hash = mocker.patch("projectx.users.api.update_session_auth_hash")

    body = json.dumps(
        {
            "current_password": "current_password",
            "password1": "password",
            "password2": "password",
        }
    )
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.change_password(request)

    assert JsonResponse.mock_calls == [mocker.call({})]
    assert authenticate.mock_calls == [
        mocker.call(username=request.user.email, password="current_password"),
        mocker.call().set_password("password"),
        mocker.call().save(),
    ]
    assert update_session_auth_hash.mock_calls == [mocker.call(request, authenticate.return_value)]


def test_change_password_bad_authentication(mocker):
    mocker.patch("projectx.users.api.authenticate", return_value=None)
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    body = json.dumps({"current_password": "current_password", "password1": "password", "password2": "password"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.change_password(request)
    assert JsonResponse.mock_calls == [
        mock.call(
            {
                "error": True,
                "errors": {
                    "current_password": ["The current password is incorrect."],
                },
            },
            status=401,
        )
    ]


def test_change_details(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    user = mock.Mock()

    body = json.dumps(
        {
            "first_name": "first_name",
            "last_name": "last_name",
        }
    )
    request = make_request(method="POST", body=body, user=user)

    api.change_details(request)

    assert JsonResponse.mock_calls == [mocker.call({})]
    assert user.mock_calls == [mocker.call.save()]

    assert user.first_name == "first_name"
    assert user.last_name == "last_name"


def test_activate_api(mocker):
    user = mock.Mock()
    data = {"user": user}
    mocker.patch("projectx.common.validation.load_data_from_schema", return_value=data)

    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")

    request = make_request(method="POST", body="{}", user=mock.Mock())

    api.activate(request)

    assert JsonResponse.mock_calls == [mock.call({"is_active": user.is_active, "user": user.to_json.return_value})]


def test_admin_su_logout_good_request(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    mocker.patch("projectx.users.api.su_logout", return_value=mock.Mock(url="/redirect_url", status_code=200))
    api.admin_su_logout(make_request())

    assert JsonResponse.mock_calls == [mock.call({"redirect_url": "/redirect_url"})]


def test_admin_su_logout_bad_request(mocker):
    JsonResponse = mocker.patch("projectx.users.api.JsonResponse")
    mocker.patch("projectx.users.api.su_logout", return_value=mock.Mock(content="content", status_code=403))
    api.admin_su_logout(make_request())

    assert JsonResponse.mock_calls == [mock.call({"error": "content"}, status=403)]
