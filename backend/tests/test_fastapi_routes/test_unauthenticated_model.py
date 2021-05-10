from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app.models import UnauthenticatedModel

from api.fastapi import RouteBuilder

BASE_PATH = "/unauthenticatedmodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    config = {"identifier": "uuid", "identifier_class": UUID}
    route_builder = RouteBuilder(
        UnauthenticatedModel,
        config=config,
    )
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_unathenticated_model_create_list_update_get_and_delete(client, mocker):
    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name"}

    response = client.get(BASE_PATH)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name"}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name"}

    response = client.put(f"{BASE_PATH}{uuid}/", json={"name": "name2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
