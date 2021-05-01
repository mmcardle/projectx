import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import RouteBuilder
from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)


API_KEY = "api_key"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key=API_KEY)


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(User, [], [])
    route_builder.add_list_route_to_router(router)
    route_builder.add_get_route_to_router(router)
    route_builder.add_create_route_to_router(router)
    route_builder.add_update_route_to_router(router)
    route_builder.add_delete_route_to_router(router)
    assert len(router.routes) == 5


@pytest.mark.django_db()
def test_bad_api_key():
    response = client.get("/api/users/user-uuid/", headers={"X-API-Key": "BAD_API_KEY"})
    assert response.status_code == 400, response.content.decode("utf-8")
    assert response.json() == {"detail": "X-API-Key header invalid."}


@pytest.mark.django_db()
def test_users_has_no_listing_api(api_key_user):
    response = client.get("/api/users/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 405, response.content


@pytest.mark.django_db(transaction=True)
def test_users_create_update_and_get(api_key_user, mocker):

    email = "test_users_create_and_retrieve@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": api_key_user.key},
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

    response = client.get(f"/api/users/{public_uuid}/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "email": email,
        "first_name": "first_name",
        "last_name": "last_name",
        "public_uuid": mocker.ANY,
    }


@pytest.mark.django_db(transaction=True)
def test_users_create_and_update(api_key_user, mocker):

    email = "test_users_create_and_update@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": api_key_user.key},
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


@pytest.mark.django_db(transaction=True)
def test_users_create_and_delete(api_key_user, mocker):

    email = "test_users_create_and_delete@tempurl.com"

    response = client.post(
        "/api/users/",
        headers={"X-API-Key": api_key_user.key},
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
