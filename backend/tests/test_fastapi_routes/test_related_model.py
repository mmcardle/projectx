from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from test_app import models

from projectx.api.fastapi import RouteBuilder

CHOICES_PATH = "/choices/"
QUESTIONS_PATH = "/questions/"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client(app, router):
    route_builder1 = RouteBuilder(models.Question, config={"identifier": "uuid", "identifier_class": UUID})
    route_builder1.add_all_routes(router)
    route_builder2 = RouteBuilder(models.Choice, config={"identifier": "uuid", "identifier_class": UUID})
    route_builder2.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_related_model_create_list_update_get_and_delete(client, mocker):
    # Create a Question
    response = client.post(QUESTIONS_PATH, json={"name": "question1"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": []}

    question_id = response.json()["uuid"]

    # Create a Choice
    response = client.post(CHOICES_PATH, json={"name": "name", "question": question_id})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "question": question_id}

    choice_id = response.json()["uuid"]

    # Get the Question
    response = client.get(f"{QUESTIONS_PATH}{question_id}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": [{"uuid": choice_id}]}

    # Get the Choice
    response = client.get(f"{CHOICES_PATH}{choice_id}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": choice_id, "name": "name", "question": question_id}

    # Get all Choices
    response = client.get(f"{CHOICES_PATH}")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"items": [{"uuid": mocker.ANY, "name": "name", "question": question_id}]}

    # Create a second Choice
    response = client.post(CHOICES_PATH, json={"name": "name", "question": question_id})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "name", "question": question_id}

    choice2_id = response.json()["uuid"]

    # Get Question, with the two choices
    response = client.get(f"{QUESTIONS_PATH}{question_id}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "uuid": mocker.ANY,
        "name": "question1",
        "choices": [{"uuid": choice_id}, {"uuid": choice2_id}],
    }

    # Create a second Question
    response = client.post(QUESTIONS_PATH, json={"name": "question1"})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": []}

    question2_id = response.json()["uuid"]

    # Get the second Question
    response = client.put(f"{CHOICES_PATH}{choice_id}/", json={"name": "name2", "question": question2_id})
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": choice_id, "question": question2_id}

    # Delete the first Choice
    response = client.delete(f"{CHOICES_PATH}{choice_id}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"name": "name2", "uuid": choice_id, "question": question2_id}

    # Ensure choice is missing
    response = client.delete(f"{CHOICES_PATH}{choice_id}/")
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {choice_id} not found."}

    # Ensure Question only has a single Choice
    response = client.get(f"{QUESTIONS_PATH}{question_id}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {"uuid": mocker.ANY, "name": "question1", "choices": [{"uuid": choice2_id}]}
