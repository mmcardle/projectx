from uuid import UUID

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from test_app.models import UnauthenticatedTestModel

from api.fastapi import RouteBuilder
from api.wsgi import application

BASE_PATH = "/unauthenticatedtestmodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client():
    app = FastAPI()
    router = APIRouter()
    config = {"identifier": "uuid", "identifier_class": UUID}
    route_builder = RouteBuilder(
        UnauthenticatedTestModel,
        config=config,
    )
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodel_create_list_and_get(client, mocker):
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
def test_testapp_testmodel_create_update_and_get(client, mocker):

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
def test_testapp_testmodel_create_and_update(client, mocker):

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
def test_testapp_testmodel_create_and_delete(client, mocker):

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
