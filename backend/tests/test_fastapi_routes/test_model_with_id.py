from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleIDModel, SimpleUUIDModel

from api.fastapi import RouteBuilder


@pytest.mark.django_db(transaction=True)
@pytest.fixture(
    name="client_and_routebuilder",
    params=[
        {"model": SimpleIDModel, "config": {}},
        {"model": SimpleUUIDModel, "config": {"identifier": "uuid", "identifier_class": UUID}},
    ],
)
def get_client(request, app, router):
    config = request.param["config"]
    route_builder = RouteBuilder(request.param["model"], config=config)
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app), route_builder


@pytest.mark.django_db(transaction=True)
def test_model_with_id_create_list_update_get_and_delete(client_and_routebuilder, mocker):

    client, route_builder = client_and_routebuilder
    model_identifier, base_path = route_builder.model_identifier, route_builder.path_for_list_and_post

    response = client.post(base_path, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: mocker.ANY, "name": "name"}

    response = client.get(base_path)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{model_identifier: mocker.ANY, "name": "name"}]}

    identifier = response.json()["items"][0][model_identifier]

    response = client.get(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name"}

    response = client.put(f"{base_path}{identifier}/", json={"name": "name2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name2"}

    identifier = response.json()[model_identifier]

    response = client.delete(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name2"}

    response = client.delete(f"{base_path}{identifier}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {identifier} not found."}
