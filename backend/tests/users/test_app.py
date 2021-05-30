from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from projectx.api.asgi import application
from projectx.users.apps import (
    UsersConfig,
    create_access_token,
    get_current_user_func,
    get_user_authentication,
)
from projectx.users.models import User

BASE_PATH = "/api/auth/"

client = TestClient(application)


def test_app():
    assert UsersConfig.name == "projectx.users"


def test_get_user_authentication():
    assert get_user_authentication()


def test_create_access_token(mocker):
    access_token_expires = timedelta(minutes=30)
    token = create_access_token({"sub": "username"}, access_token_expires)
    get_user = mocker.Mock()
    get_current_user = get_current_user_func(get_user)
    get_current_user(token)

    assert get_user.mock_calls == [mocker.call(username="username")]


def test_create_access_token_bad_jwt(mocker):
    access_token_expires = timedelta(minutes=30)
    token = create_access_token({"sub": None}, access_token_expires)
    get_user = mocker.Mock()
    get_current_user = get_current_user_func(get_user)
    with pytest.raises(HTTPException) as http_error:
        get_current_user(token)

    assert http_error.value.status_code == 401
    assert http_error.value.detail == "Could not validate credentials - bad token"


def test_create_access_token_no_username(mocker):
    access_token_expires = timedelta(minutes=30)
    token = create_access_token({"sub": ""}, access_token_expires)
    get_user = mocker.Mock()
    get_current_user = get_current_user_func(get_user)
    with pytest.raises(HTTPException) as http_error:
        get_current_user(token)

    assert http_error.value.status_code == 401
    assert http_error.value.detail == "Could not validate credentials - empty username"


def test_create_access_token_no_user(mocker):
    access_token_expires = timedelta(minutes=30)
    token = create_access_token({"sub": "username"}, access_token_expires)
    get_user = mocker.Mock(return_value=None)
    get_current_user = get_current_user_func(get_user)
    with pytest.raises(HTTPException) as http_error:
        get_current_user(token)

    assert http_error.value.status_code == 401
    assert http_error.value.detail == "Could not validate credentials - no such user"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="user")
def user_fixture():
    return User.objects.create_user(
        email="user_fixture@tempurl.com", first_name="Test", last_name="User", password="password"
    )


@pytest.mark.django_db(transaction=True)
def test_testapp_auth_and_get(user, mocker):

    response = client.post(
        f"{BASE_PATH}token/",
        data={"username": user.username, "password": "password"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }

    access_token = response.json()["access_token"]

    response = client.get(
        f"{BASE_PATH}self/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": "user_fixture@tempurl.com",
        "first_name": "Test",
        "is_active": True,
        "last_name": "User",
        "public_uuid": mocker.ANY,
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_auth__with_bad_password(user):

    response = client.post(
        f"{BASE_PATH}token/",
        data={"username": user.username, "password": "bad_password"},
    )
    assert response.status_code == 401, response.content.decode("utf-8")
    assert response.json() == {
        "detail": "Incorrect username or password",
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_auth_with_inactive_user(user, mocker):

    response = client.post(
        f"{BASE_PATH}token/",
        data={"username": user.username, "password": "password"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }

    user.is_active = False
    user.save()

    access_token = response.json()["access_token"]

    response = client.get(
        f"{BASE_PATH}self/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {
        "detail": "Inactive user",
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_auth_with_deleted_user(user, mocker):

    response = client.post(
        f"{BASE_PATH}token/",
        data={"username": user.username, "password": "password"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }

    user.delete()

    access_token = response.json()["access_token"]

    response = client.get(
        f"{BASE_PATH}self/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401, response.content.decode("utf-8")
    assert response.json() == {
        "detail": "Could not validate credentials - no such user",
    }
