import pytest
from fastapi.testclient import TestClient
from test_app.models import ModelWithValidation

from api.fastapi import RouteBuilder


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client_and_routebuilder")
def get_client(app, router):
    route_builder = RouteBuilder(ModelWithValidation)
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app), route_builder


@pytest.mark.django_db(transaction=True)
def test_model_with_validation(client_and_routebuilder):

    client, route_builder = client_and_routebuilder

    response = client.get(route_builder.path_for_list_and_post)
    response = client.post(route_builder.path_for_list_and_post, json={"number": "12"})
    assert response.status_code == 422, response.content.decode("utf-8")
