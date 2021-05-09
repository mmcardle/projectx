from uuid import UUID

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from test_app import models

from api.fastapi import RouteBuilder

BASE_PATH = "/choices/"
BASE_PATH_RELATED = "/questions/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client():
    app = FastAPI()
    router = APIRouter()
    route_builder1 = RouteBuilder(models.Question, config={"identifier": "uuid", "identifier_class": UUID})
    route_builder1.add_all_routes(router)
    route_builder2 = RouteBuilder(models.Choice, config={"identifier": "uuid", "identifier_class": UUID})
    route_builder2.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_related_model_create_list_update_get_and_delete(client, mocker):

    response = client.post(BASE_PATH_RELATED, json={"name": "question1"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": []}

    question_id = response.json()["uuid"]

    response = client.post(BASE_PATH, json={"name": "name", "question": question_id})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "question": question_id}

    response = client.get(f"{BASE_PATH}")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name", "question": question_id}]}

    uuid = response.json()["items"][0]["uuid"]

    response = client.get(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": uuid, "name": "name", "question": question_id}

    response = client.post(BASE_PATH_RELATED, json={"name": "question1"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": []}

    question2_id = response.json()["uuid"]

    response = client.put(f"{BASE_PATH}{uuid}/", json={"name": "name2", "question": question2_id})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid, "question": question2_id}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": uuid, "question": question2_id}

    response = client.delete(f"{BASE_PATH}{uuid}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
