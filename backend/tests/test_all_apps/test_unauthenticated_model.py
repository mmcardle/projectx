import pytest
from fastapi.testclient import TestClient

from api.wsgi import application

client = TestClient(application)

BASE_PATH = "/api/unauthenticatedtestmodels/"


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_list_and_get(mocker):
    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    response = client.get(BASE_PATH)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name"}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_update_and_get(mocker):

    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    uuid = response.json()["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": uuid,
        "name": "name",
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_update(mocker):

    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "name",
    }

    uuid = response.json()["uuid"]

    response = client.put(f"{BASE_PATH}{uuid}/", json={"name": "name2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name2",
        "uuid": uuid,
    }


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_and_delete(mocker):

    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    uuid = response.json()["uuid"]

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": uuid,
    }

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
