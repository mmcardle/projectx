import pytest
from django.db.models import Q
from fastapi.testclient import TestClient
from test_app.models import SimpleModel

from projectx.api.fastapi import RouteBuilder

BASE_PATH = "/simplemodels/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    def filter_by_name(_):
        return Q(name__contains="XXX")

    route_builder = RouteBuilder(
        SimpleModel, request_fields=["name"], response_fields=["name"], query_filter=filter_by_name
    )
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="simple_model1")
def create_simple_model_1():
    return SimpleModel.objects.create(name="XXX - Should appear in response")


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="simple_model2")
def create_simple_model_2():
    return SimpleModel.objects.create(name="YYY - Should NOT appear in response")


@pytest.mark.django_db(transaction=True)
def test_filtering_with_list(client, simple_model1, simple_model2):

    assert simple_model2

    response = client.get(BASE_PATH)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"name": simple_model1.name}]}


@pytest.mark.django_db(transaction=True)
def test_filtering_with_get(client, simple_model1, simple_model2):

    response = client.get(f"{BASE_PATH}{simple_model1.pk}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "XXX - Should appear in response"}

    response = client.get(f"{BASE_PATH}{simple_model2.pk}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}


@pytest.mark.django_db(transaction=True)
def test_filtering_with_patch(client, simple_model1, simple_model2):

    response = client.patch(f"{BASE_PATH}{simple_model1.pk}/", json={"name": "new_name - Should appear in response"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "new_name - Should appear in response"}

    response = client.patch(f"{BASE_PATH}{simple_model2.pk}/", json={"name": "new_name"})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}


@pytest.mark.django_db(transaction=True)
def test_filtering_with_put(client, simple_model1, simple_model2):

    response = client.put(f"{BASE_PATH}{simple_model1.pk}/", json={"name": "new_name - Should appear in response"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "new_name - Should appear in response"}

    response = client.put(f"{BASE_PATH}{simple_model2.pk}/", json={"name": "new_name"})
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}


@pytest.mark.django_db(transaction=True)
def test_filtering_with_delete(client, simple_model1, simple_model2):

    response = client.delete(f"{BASE_PATH}{simple_model1.pk}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "XXX - Should appear in response"}

    response = client.delete(f"{BASE_PATH}{simple_model2.pk}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": "Object not found."}
