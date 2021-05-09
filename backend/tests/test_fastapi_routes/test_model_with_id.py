import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from test_app.models import SimpleIDModel

from api.fastapi import RouteBuilder

BASE_PATH = "/simpleidmodels/"

PRIMARY_KEY = SimpleIDModel._meta.pk.name


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client():
    app = FastAPI()
    router = APIRouter()
    route_builder = RouteBuilder(SimpleIDModel)
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_model_with_id_create_list_update_get_and_delete(client, mocker):
    response = client.post(BASE_PATH, json={"name": "name"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {PRIMARY_KEY: mocker.ANY, "name": "name"}

    response = client.get(BASE_PATH)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{PRIMARY_KEY: mocker.ANY, "name": "name"}]}

    identifier = response.json()["items"][0][PRIMARY_KEY]

    response = client.get(f"{BASE_PATH}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {PRIMARY_KEY: identifier, "name": "name"}

    response = client.put(f"{BASE_PATH}{identifier}/", json={"name": "name2"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {PRIMARY_KEY: identifier, "name": "name2"}

    identifier = response.json()[PRIMARY_KEY]

    response = client.delete(f"{BASE_PATH}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {PRIMARY_KEY: identifier, "name": "name2"}

    response = client.delete(f"{BASE_PATH}{identifier}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {identifier} not found."}
