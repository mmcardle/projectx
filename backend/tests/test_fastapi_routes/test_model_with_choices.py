import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_app.models import SimpleModelWithChoices

from projectx.api.fastapi import RouteBuilder


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client_and_routebuilder")
def get_client(app, router):
    route_builder = RouteBuilder(SimpleModelWithChoices)
    route_builder.add_all_routes(router)
    app.include_router(router)

    application = FastAPI(
        title="ProjectX",
        description="ProjectX Demo",
        version="0.0.1",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/v1/openapi.json",
    )

    application.include_router(router, prefix="/api")

    application.openapi()
    return TestClient(app), route_builder


@pytest.mark.django_db(transaction=True)
def test_model_with_choices_create_list_update_get(client_and_routebuilder, mocker):
    client, route_builder = client_and_routebuilder
    model_identifier, base_path = route_builder.model_identifier, route_builder.path_for_list_and_post

    response = client.post(base_path, json={"choice": "CHOICE1"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: mocker.ANY, "choice": "CHOICE1"}

    response = client.get(base_path)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{model_identifier: mocker.ANY, "choice": "CHOICE1"}]}

    identifier = response.json()["items"][0][model_identifier]

    response = client.get(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "choice": "CHOICE1"}

    response = client.put(f"{base_path}{identifier}/", json={"choice": "CHOICE2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "choice": "CHOICE2"}

    response = client.put(f"{base_path}{identifier}/", json={"choice": "Choice3"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {model_identifier: identifier, "choice": "Choice3"}
