import json
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ratelimit.exceptions import Ratelimited

from users import api, models

counter = 0


def make_request(**kwargs):
    if "META" not in kwargs:
        kwargs["META"] = {}

    if "REMOTE_ADDR" not in kwargs["META"]:
        # In order to not get hit by rate limits during tests we
        # have to make each request unique by adding a counter
        global counter
        kwargs["META"]["REMOTE_ADDR"] = "127.0.0.%s" % counter
        counter = counter + 1

    if "session" not in kwargs:
        kwargs["session"] = mock.Mock(get=mock.Mock(return_value=[]))

    return mock.Mock(spec=HttpRequest, **kwargs)


def test_request_is_sudo():
    assert api._request_is_sudo(make_request(session=mock.Mock(get=mock.Mock(return_value=[1]))))
    assert not api._request_is_sudo(make_request())


def test_get_logout_url_normal_request():
    assert api._get_logout_url(make_request()) == "/api/users/logout/"


def test_get_logout_url_su_request():
    su_request = make_request(
        session=mock.Mock(get=mock.Mock(return_value=[1]))
    )
    assert api._get_logout_url(su_request) == "/admin/su/logout/"


def test_user_authenticated(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")
    mocker.patch("users.api._get_token", return_value="token")

    user = mock.Mock()
    request = make_request(user=user)
    api.user(request)

    assert JsonResponse.mock_calls == [
        mock.call({
            "user": user.to_json(),
            "token": "token",
            "logout_url": "/api/users/logout/"
        })
    ]


def test_user_unauthenticated(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")

    user = mock.Mock(is_authenticated=False)
    request = make_request(user=user)
    api.user(request)

    assert JsonResponse.mock_calls == [
        mock.call({"user": None})
    ]


def test_login_GET(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")
    mocker.patch("users.api._get_token", return_value="token")

    user = mock.Mock(is_authenticated=False)
    request = make_request(method="GET", user=user, META={"CSRF_COOKIE": "token"})
    api.login(request)
    assert JsonResponse.mock_calls[0] == mock.call({"token": "token"})


def test_login_POST_rate_limited(mocker):

    mocker.patch("users.api.JsonResponse")
    mocker.patch("users.api.authenticate")
    mocker.patch("users.api.django_login")

    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST", user=user, body="{}",
        META={"CSRF_COOKIE": "token", "REMOTE_ADDR": "127.0.0.1"},
        session=mock.MagicMock()
    )
    with pytest.raises(Ratelimited) as rate_limit_ex:
        for i in range(0, 6):
            api.login(request)

    assert str(rate_limit_ex.value) == ""


def test_login_GET_no_csrf(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")

    user = mock.Mock(is_authenticated=False)
    request = make_request(method="GET", user=user)
    api.login(request)
    assert JsonResponse.mock_calls[0] == mock.call({"token": mock.ANY})


def test_login_POST(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")
    authenticate = mocker.patch("users.api.authenticate")
    django_login = mocker.patch("users.api.django_login")

    body = json.dumps(dict(email="email@none.com", password="password"))
    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST", user=user, body=body,
        META={"CSRF_COOKIE": "token"},
    )
    api.login(request)

    assert authenticate.call_args_list == [
        mock.call(request, username="email@none.com", password="password"),
    ]
    assert JsonResponse.call_args_list[0:1] == [
        mock.call({
            "success": True,
            "user": authenticate().to_json(),
            "token": mock.ANY,
            "logout_url": "/api/users/logout/"
        })
    ]
    assert django_login.mock_calls == [
        mock.call(request, authenticate())
    ]


def test_login_POST_bad_auth_with_no_user(mocker):

    UserModel = get_user_model()

    mocker.patch.object(UserModel._default_manager, "get_by_natural_key", mock.Mock(side_effect=UserModel.DoesNotExist))
    mocker.patch.object(UserModel.objects, "get", mock.Mock(side_effect=UserModel.DoesNotExist))

    JsonResponse = mocker.patch("users.api.JsonResponse")
    authenticate = mocker.patch("users.api.authenticate")
    authenticate.return_value = None
    django_login = mocker.patch("users.api.django_login")

    body = json.dumps(dict(email="email@none.com", password="password"))
    user = mock.Mock(is_authenticated=False)
    request = make_request(
        method="POST", user=user, body=body,
        META={"CSRF_COOKIE": "token"},
    )
    api.login(request)
    assert JsonResponse.mock_calls[0:1] == [
        mock.call({
            "success": False,
        }, status=401)
    ]
    assert authenticate.mock_calls == [
        mock.call(request, username="email@none.com", password="password")
    ]
    assert django_login.mock_calls == []


def test_logout(mocker):

    django_logout = mocker.patch("users.api.django_logout")
    JsonResponse = mocker.patch("users.api.JsonResponse")

    user = mock.Mock(is_authenticated=True)
    request = make_request(method="GET", user=user, path="http://127.0.0.1/path")
    api.logout(request)
    assert JsonResponse.mock_calls == [mock.call({"success": True})]
    assert django_logout.mock_calls == [mock.call(request)]


def test_reset_password(mocker):

    User = mocker.patch("users.api.models.User")
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({"email": "email"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password(request)
    assert JsonResponse.mock_calls == [
        mock.call({})
    ]
    assert User.mock_calls == [
        mock.call.reset_email("email")
    ]


def test_reset_password_no_such_email(mocker):

    user = mock.Mock()
    User = mock.Mock(
        objects=mock.Mock(
            filter=mock.Mock(
                return_value=mock.Mock(
                    exists=mock.Mock(return_value=False)
                )
            )
        )
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({"email": "nosuchemail"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password(request)
    assert JsonResponse.mock_calls == [
        mock.call({})
    ]
    assert user.mock_calls == []


def test_reset_password_bad_data(mocker):
    JsonResponse = mocker.patch("users.api.JsonResponse")
    request = make_request(method="POST", body="xxx", user=mock.Mock())
    api.reset_password(request)
    assert JsonResponse.mock_calls == [
        mock.call({"error": True}, status=401)
    ]


def test_reset_password_check(mocker):

    load_data_from_schema = mocker.patch("users.api.load_data_from_schema")

    user = mock.Mock(name="u")
    User = mock.Mock(
        check_reset_key=lambda key: (user, None)
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({"email": "email"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_check(request)
    assert JsonResponse.mock_calls == [
        mock.call({"email": user.email})
    ]

    assert load_data_from_schema.mock_calls == [
        mock.call(
            api.reset_check_schema, {"email": "email"}
        ),
        mock.call().get("reset_key")
    ]


def test_reset_password_check_bad_data(mocker):

    user = mock.Mock(name="u")
    User = mock.Mock(
        check_reset_key=lambda key: (user, None)
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({"k": "v"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_check(request)
    assert JsonResponse.mock_calls == [
        mock.call({
            "error": True,
            "errors": {
                "reset_key": ["Missing data for required field."],
                "k": ["Unknown field."]
            }
        }, status=401)
    ]


def test_reset_password_check_user_is_None(mocker):

    load_data_from_schema = mocker.patch("users.api.load_data_from_schema")

    User = mock.Mock(
        check_reset_key=lambda key: (None, "error")
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({"email": "email"})
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_check(request)
    assert JsonResponse.mock_calls == [
        mock.call({"error": "error"}, status=401)
    ]

    assert load_data_from_schema.mock_calls == [
        mock.call(
            api.reset_check_schema, {"email": "email"}
        ),
        mock.call().get("reset_key")
    ]


def test_reset_password_complete(mocker):

    load_data_from_schema = mocker.patch("users.api.load_data_from_schema")

    user = mock.Mock()
    User = mock.Mock(
        check_reset_key=lambda key: (user, None)
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({
        "reset_key": "reset_key",
        "password1": "password1_value",
        "password2": "password2_value"
    })
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_complete(request)
    assert JsonResponse.mock_calls == [
        mock.call(user.to_json.return_value)
    ]

    assert load_data_from_schema.mock_calls == [
        mock.call(
            api.reset_password_schema,
            {
                "reset_key": "reset_key",
                "password1": "password1_value",
                "password2": "password2_value"
            }
        ),
        mock.call().get("reset_key"),
        mock.call().get("password1")
    ]
    expected_password = (
        load_data_from_schema.return_value.get.return_value
    )
    assert user.mock_calls == [
        mock.call.set_password(expected_password),
        mock.call.save(),
        mock.call.delete_reset_key(user.email),
        mock.call.to_json()
    ]


def test_reset_password_complete_bad_data(mocker):

    User = mock.Mock(
        check_reset_key=lambda key: (None, "error")
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({
        "xxx": "xxx",
    })
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_complete(request)
    assert JsonResponse.mock_calls == [
        mock.call({
            "error": True,
            "errors": {
                "password1": ["Missing data for required field."],
                "password2": ["Missing data for required field."],
                "reset_key": ["Missing data for required field."],
                "xxx": ["Unknown field."]
            }
        }, status=401)
    ]


def test_reset_password_complete_no_user(mocker):

    load_data_from_schema = mocker.patch("users.api.load_data_from_schema")

    User = mock.Mock(
        check_reset_key=lambda key: (None, "error")
    )
    user_models = mocker.patch("users.api.models")
    user_models.User = User
    JsonResponse = mocker.patch("users.api.JsonResponse")

    body = json.dumps({
        "password1": "password1",
        "password2": "password2"
    })
    request = make_request(method="POST", body=body, user=mock.Mock())

    api.reset_password_complete(request)
    assert JsonResponse.mock_calls == [
        mock.call({"error": "error"}, status=401)
    ]

    assert load_data_from_schema.mock_calls == [
        mock.call(
            api.reset_password_schema,
            {
                "password1": "password1",
                "password2": "password2"
            }
        ),
        mock.call().get("reset_key")
    ]


def test_activate_check_api(mocker):

    user = mock.Mock()
    data = {"user": user}
    mocker.patch("common.validation.load_data_from_schema", return_value=data)

    JsonResponse = mocker.patch("users.api.JsonResponse")

    request = make_request(method="POST", body="{}", user=mock.Mock())

    api.activate_check(request)

    assert JsonResponse.mock_calls == [
        mock.call({"is_active": user.is_active, "user": user.to_json.return_value})
    ]


def test_activate_api(mocker):

    user = mock.Mock()
    data = {
        "user": user,
        "username": "username",
        "first_name": "first_name",
        "last_name": "last_name",
        "password1": "password1",
    }
    mocker.patch("common.validation.load_data_from_schema", return_value=data)

    JsonResponse = mocker.patch("users.api.JsonResponse")

    request = make_request(method="POST", body="{}", user=mock.Mock())

    api.activate(request)

    assert user.mock_calls == [
        mocker.call.set_password("password1"),
        mocker.call.activate(),
        mocker.call.delete_activate_key(user.email),
        mocker.call.to_json(),
    ]

    assert user.username == "username"
    assert user.first_name == "first_name"
    assert user.last_name == "last_name"

    assert JsonResponse.mock_calls == [
        mock.call(user.to_json.return_value)
    ]


def test_admin_su_logout_good_request(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")
    su_logout = mocker.patch(
        "users.api.su_logout", return_value=mock.Mock(url="/redirect_url", status_code=200)
    )
    response = api.admin_su_logout(make_request())

    assert JsonResponse.mock_calls == [mock.call({"redirect_url": "/redirect_url"})]


def test_admin_su_logout_bad_request(mocker):

    JsonResponse = mocker.patch("users.api.JsonResponse")
    su_logout = mocker.patch(
        "users.api.su_logout", return_value=mock.Mock(content="content", status_code=403)
    )
    response = api.admin_su_logout(make_request())

    assert JsonResponse.mock_calls == [mock.call({"error": "content"}, status=403)]
