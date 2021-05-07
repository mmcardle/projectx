import pytest
from fastapi.testclient import TestClient

from api.wsgi import application
from test_app1 import models
from users.models import ApiKey, User

client = TestClient(application)

BASE_PATH = "/api/testmodelwithrelationships/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key="api_key")


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="related_model")
def create_related_model():
    return models.RelatedModel.objects.create(name="related_model")


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_list_and_get(related_model, api_key_user, mocker):

    response = client.post(
        f"{BASE_PATH}",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}

    response = client.get(f"{BASE_PATH}", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name", "related_model": related_model.id}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_update_and_get(related_model, api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}

    uuid = response.json()["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name", "related_model": related_model.id}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_update(related_model, api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}

    uuid = response.json()["uuid"]

    response = client.put(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name2", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid, "related_model": related_model.id}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_delete(related_model, api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
        "related_model": related_model.id,
    }

    uuid = response.json()["uuid"]

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name", "uuid": uuid, "related_model": related_model.id}

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithowner_create_list_and_get(related_model, api_key_user, mocker):

    response = client.post(
        BASE_PATH,
        headers={"X-API-Key": api_key_user.key},
        json={"name": "name", "related_model": related_model.id},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}

    response = client.get(BASE_PATH, headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name", "related_model": related_model.id}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/", headers={"X-API-Key": api_key_user.key})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
        "related_model": related_model.id,
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": uuid,
        "related_model": related_model.id,
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"X-API-Key": api_key_user.key},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
