from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleModelWithOwner

from projectx.api.fastapi import RouteBuilder, check_api_key
from projectx.users.models import ApiKey, User

BASE_PATH = "/simplemodelwithowners/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    config = {"identifier": "uuid", "identifier_class": UUID}
    route_builder = RouteBuilder(
        SimpleModelWithOwner,
        request_fields=["name"],
        response_fields=["name", "uuid"],
        config=config,
        owner_field="owner",
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


@pytest.mark.django_db(transaction=True)
def test_model_with_owner_create_list_update_patch_get_and_delete(client, api_key_user, mocker):
    response = client.post(BASE_PATH, headers={"X-API-Key": api_key_user.key}, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name"}

    response = client.get(BASE_PATH, headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name"}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name"}

    response = client.put(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key}, json={"name": "name2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid}

    response = client.patch(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key}, json={"name": "name3"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name3", "uuid": uuid}

    response = client.delete(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name3", "uuid": uuid}

    response = client.delete(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_other_user_cannot_access(client, api_key_user, mocker):
    response = client.post(BASE_PATH, headers={"X-API-Key": api_key_user.key}, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name"}

    uuid = response.json()["uuid"]

    other_user = User.objects.create_user(
        email="apikeyuser2@tempurl.com", first_name="Other API", last_name="Test User"
    )
    api_key_other_user = ApiKey.objects.create(user=other_user, key="api_key_other_user")

    response = client.get(
        BASE_PATH,
        headers={"X-API-Key": api_key_other_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": []}

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_other_user.key})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}

    response = client.put(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_other_user.key},
        json={"name": "Should not be able to set this!"},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}

    response = client.patch(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_other_user.key},
        json={"name": "Should not be able to set this!"},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}

    response = client.delete(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_other_user.key})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}
