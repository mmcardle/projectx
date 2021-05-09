import pytest
from fastapi.testclient import TestClient

from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)

BASE_PATH = "/api/testmodelwithowners/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_create_list_and_get(api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    response = client.get(BASE_PATH, headers={"X-API-Key": api_key_user.key})
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

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": uuid,
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_other_user_cannot_get(api_key_user, mocker):

    response = client.post(
        BASE_PATH,
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

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_other_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}
