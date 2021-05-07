import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import RouteBuilder
from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)

BASE_PATH = "/api/testmodels/"
JWT_USER_PASSWORD = "jwtpassword"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="jwt_user")
def jwt_user_fixture():
    return User.objects.create_user(
        email="jwt_user@tempurl.com", first_name="JWT", last_name="Test User", password=JWT_USER_PASSWORD
    )


@pytest.mark.django_db()
def test_bad_api_key():
    response = client.get("/api/testmodels/uuid/", headers={"X-API-Key": "BAD_API_KEY"})
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


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_create_list_and_get(api_key_user, mocker):

    response = client.post(
        "/api/testmodelwithowners/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    response = client.get("/api/testmodelwithowners/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [
            {
                "uuid": mocker.ANY,
                "name": "name",
            }
        ]
    }

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"/api/testmodelwithowners/{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
    }

    response = client.delete(
        f"/api/testmodelwithowners/{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": uuid,
    }

    response = client.delete(
        f"/api/testmodelwithowners/{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_other_user_cannot_get(api_key_user, mocker):

    response = client.post(
        "/api/testmodelwithowners/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    uuid = response.json()["uuid"]

    other_user = User.objects.create_user(
        email="apikeyuser2@tempurl.com", first_name="Other API", last_name="Test User"
    )
    api_key_other_user = ApiKey.objects.create(user=other_user, key="api_key_other_user")

    response = client.get(
        "/api/testmodelwithowners/",
        headers={"X-API-Key": api_key_other_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": []}

    response = client.get(f"/api/testmodelwithowners/{uuid}/", headers={"X-API-Key": api_key_other_user.key})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}

    response = client.put(
        f"/api/testmodelwithowners/{uuid}/",
        headers={"X-API-Key": api_key_other_user.key},
        json={"name": "Should not be able to set this!"},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}

    response = client.delete(
        f"/api/testmodelwithowners/{uuid}/",
        headers={"X-API-Key": api_key_other_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithjwt_not_authenticated(api_key_user):

    response = client.post(
        "/api/testmodelwithjwts/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 401, response.content.decode("utf-8")
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithjwt_create_get_and_delete(jwt_user, mocker):

    response = client.post(
        "/api/auth/token/",
        data={"username": jwt_user.username, "password": JWT_USER_PASSWORD},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }

    access_token = response.json()["access_token"]

    response = client.post(
        "/api/testmodelwithjwts/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    uuid = response.json()["uuid"]

    response = client.get(
        f"/api/testmodelwithjwts/{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    response = client.delete(
        f"/api/testmodelwithjwts/{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    response = client.get(
        f"/api/testmodelwithjwts/{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
