import pytest
from fastapi.testclient import TestClient

from api.wsgi import application

client = TestClient(application)


API_KEY = "api_key"


@pytest.mark.parametrize(
    "path",
    [
        "/api/users/",
        "/api/users/user-uuid/",
    ],
)
@pytest.mark.django_db
def test_bad_api_key(path):
    response = client.get(path, headers={"X-API-Key": "BAD_API_KEY"})
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {"detail": "X-API-Key header invalid."}


@pytest.mark.django_db
def test_no_api_key():
    response = client.get("/api/users/")
    assert response.status_code == 422, response.content.decode("utf-8")
    assert response.json() == {
        "detail": [{"loc": ["header", "x-api-key"], "msg": "field required", "type": "value_error.missing"}],
    }


@pytest.mark.django_db
def test_users_empty():
    response = client.get("/api/users/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert response.json() == {"items": []}


@pytest.mark.django_db
def test_users_create_update_and_get(mocker):

    email = "test_users_create_and_retrieve@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": API_KEY},
        json={"email": email, "first_name": "first_name", "last_name": "last_name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }

    response = client.get("/api/users/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [{"email": email, "first_name": "first_name", "last_name": "last_name", "public_uuid": mocker.ANY}]
    }

    public_uuid = response.json()["items"][0]["public_uuid"]

    response = client.get(f"/api/users/{public_uuid}/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }


@pytest.mark.django_db
def test_users_create_and_update(mocker):

    email = "test_users_create_and_update@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": API_KEY},
        json={"email": email, "first_name": "first_name", "last_name": "last_name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }

    public_uuid = response.json()["public_uuid"]

    response = client.put(
        f"/api/users/{public_uuid}/",
        headers={"X-API-Key": API_KEY},
        json={"email": email, "first_name": "first_name2", "last_name": "last_name2"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name2",
        "last_name": "last_name2",
        "public_uuid": mocker.ANY,
    }


@pytest.mark.django_db
def test_users_create_and_delete(mocker):

    email = "test_users_create_and_delete@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": API_KEY},
        json={"email": email, "first_name": "first_name", "last_name": "last_name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }

    user_uuid = response.json()["public_uuid"]

    response = client.delete(
        f"/api/users/{user_uuid}/",
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }

    response = client.delete(
        f"/api/users/{user_uuid}/",
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {user_uuid} not found."}
