from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleModel

from projectx.api.fastapi import RouteBuilder

BASE_PATH = "/simplemodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    route_builder = RouteBuilder(
        SimpleModel,
        config={"identifier": "uuid", "identifier_class": UUID},
    )
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_create_and_patch(client, mocker):
    response = client.post(
        BASE_PATH,
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

    response = client.patch(
        f"{BASE_PATH}{uuid}/",
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
        json={"config": {"k2": "v2"}},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name2",
        "uuid": uuid,
        "created": mocker.ANY,
        "last_updated": mocker.ANY,
        "config": {"k2": "v2"},
    }
