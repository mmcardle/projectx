from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app import models

from projectx.api.fastapi import RouteBuilder

BASE_PATH = "/pizzas/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    config = {"identifier": "uuid", "identifier_class": UUID}
    route_builder1 = RouteBuilder(models.Pizza, config=config)
    route_builder1.add_all_routes(router)
    route_builder2 = RouteBuilder(models.Topping, config=config)
    route_builder2.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="topping")
def create_topping():
    return models.Topping.objects.create(name="topping")


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="topping2")
def create_topping2():
    return models.Topping.objects.create(name="topping2")


@pytest.mark.django_db(transaction=True)
def test_related_model_with_m2m_create_list_update_get_and_delete(client, topping, topping2, mocker):
    response = client.post(BASE_PATH, json={"name": "name", "toppings": [{"uuid": str(topping.pk)}]})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "toppings": [{"uuid": str(topping.pk)}]}

    response = client.get(f"{BASE_PATH}")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name", "toppings": [{"uuid": str(topping.pk)}]}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name", "toppings": [{"uuid": str(topping.pk)}]}

    response = client.put(f"{BASE_PATH}{uuid}/", json={"name": "name2", "toppings": [{"uuid": str(topping2.pk)}]})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid, "toppings": [{"uuid": str(topping2.pk)}]}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid, "toppings": [{"uuid": str(topping2.pk)}]}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
