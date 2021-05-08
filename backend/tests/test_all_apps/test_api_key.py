import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import RouteBuilder
from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)

BASE_PATH = "/api/testmodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


@pytest.mark.django_db()
def test_bad_api_key():
    response = client.get(f"{BASE_PATH}uuid/", headers={"X-API-Key": "BAD_API_KEY"})
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {"detail": "X-API-Key header invalid."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_list_and_get(api_key_user, mocker):
    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    response = client.get(BASE_PATH, headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [{"uuid": mocker.ANY, "name": "name", "created": mocker.ANY, "last_updated": mocker.ANY, "config": {}}]
    }

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_update_and_get(api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    uuid = response.json()["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_update(api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    uuid = response.json()["uuid"]

    response = client.put(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name2"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name2",
        "uuid": uuid,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_delete(api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    uuid = response.json()["uuid"]

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": uuid,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
