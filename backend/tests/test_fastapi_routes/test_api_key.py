from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleModel

from projectx.api.fastapi import RouteBuilder, check_api_key
from projectx.users.models import ApiKey, User

BASE_PATH = "/simplemodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    route_builder = RouteBuilder(
        SimpleModel,
        config={"identifier": "uuid", "identifier_class": UUID},
        authentication=check_api_key,
    )
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


@pytest.mark.django_db()
def test_bad_api_key(client):
    response = client.get(f"{BASE_PATH}uuid/", headers={"X-API-Key": "BAD_API_KEY"})
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {"detail": "X-API-Key header invalid."}


@pytest.mark.django_db(transaction=True)
def test_api_key_create_list_update_get_and_delete(client, api_key_user, mocker):
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

    response = client.patch(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name3"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name3",
        "uuid": uuid,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name3",
        "uuid": uuid,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }

    response = client.get(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
