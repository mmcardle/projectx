import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleModelWithArray

from projectx.api.fastapi import RouteBuilder


@pytest.mark.django_db(transaction=True)
@pytest.fixture(
    name="client_and_routebuilder",
    params=[
        {"model": SimpleModelWithArray, "config": {}},
    ],
)
def get_client(request, app, router):
    config = request.param["config"]
    route_builder = RouteBuilder(request.param["model"], config=config)
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app), route_builder


@pytest.mark.django_db(transaction=True)
def test_model_with_array_create_list_update_get_and_delete(client_and_routebuilder, mocker):
    client, route_builder = client_and_routebuilder
    model_identifier, base_path = route_builder.model_identifier, route_builder.path_for_list_and_post

    response = client.post(base_path, json={"name": "name", "an_array": ["a", "b"]})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: mocker.ANY, "name": "name", "an_array": ["a", "b"]}

    response = client.get(base_path)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{model_identifier: mocker.ANY, "name": "name", "an_array": ["a", "b"]}]}

    identifier = response.json()["items"][0][model_identifier]

    response = client.get(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name", "an_array": ["a", "b"]}

    response = client.put(f"{base_path}{identifier}/", json={"name": "name2", "an_array": ["c", "d"]})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name2", "an_array": ["c", "d"]}

    identifier = response.json()[model_identifier]

    response = client.delete(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "name": "name2", "an_array": ["c", "d"]}

    response = client.delete(f"{base_path}{identifier}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {identifier} not found."}
