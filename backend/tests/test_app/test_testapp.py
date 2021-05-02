import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import RouteBuilder
from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(User, [], [], [])
    route_builder.add_list_route_to_router(router)
    route_builder.add_get_route_to_router(router)
    route_builder.add_create_route_to_router(router)
    route_builder.add_update_route_to_router(router)
    route_builder.add_delete_route_to_router(router)
    assert len(router.routes) == 5


@pytest.mark.django_db()
def test_bad_api_key():
    response = client.get("/api/testmodels/uuid/", headers={"X-API-Key": "BAD_API_KEY"})
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {"detail": "X-API-Key header invalid."}


@pytest.mark.django_db(transaction=True)
def test_testapp_create_and_get(api_key_user, mocker):

    response = client.post(
        "/api/testmodels/",
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

    response = client.get("/api/testmodels/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [{"uuid": mocker.ANY, "name": "name", "created": mocker.ANY, "last_updated": mocker.ANY, "config": {}}]
    }

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"/api/testmodels/{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_create_update_and_get(api_key_user, mocker):

    response = client.post(
        "/api/testmodels/",
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

    response = client.get(f"/api/testmodels/{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {},
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_create_and_update(api_key_user, mocker):

    response = client.post(
        "/api/testmodels/",
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
        f"/api/testmodels/{uuid}/",
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
def test_testapp_create_and_delete(api_key_user, mocker):

    response = client.post(
        "/api/testmodels/",
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
        f"/api/testmodels/{uuid}/",
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
        f"/api/testmodels/{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
