import pytest
from fastapi.testclient import TestClient
from test_app.models import SimpleModelWithDefaultFields

from projectx.api.fastapi import RouteBuilder


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client_and_routebuilder")
def get_client(app, router):
    route_builder = RouteBuilder(SimpleModelWithDefaultFields)
    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app), route_builder


@pytest.mark.django_db(transaction=True)
def test_model_with_default_create_list_get(client_and_routebuilder, mocker):
    client, route_builder = client_and_routebuilder
    model_identifier, base_path = route_builder.model_identifier, route_builder.path_for_list_and_post

    response = client.post(
        base_path,
        json={
            "request_field_with_default": "request_field_with_default",
            "request_field_with_no_default": "request_field_with_no_default",
            "json_field_with_default": {"key": "value"},
        },
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        model_identifier: mocker.ANY,
        "field_with_blank_true": "",
        "hidden_field_with_default": "Default",
        "field_with_blank_true_and_default": "field_with_blank_true_and_default",
        "request_field_with_default": "request_field_with_default",
        "request_field_with_no_default": "request_field_with_no_default",
        "json_field_with_default": {"key": "value"},
    }

    response = client.get(base_path)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [
            {
                model_identifier: mocker.ANY,
                "field_with_blank_true": "",
                "field_with_blank_true_and_default": "field_with_blank_true_and_default",
                "hidden_field_with_default": "Default",
                "request_field_with_default": "request_field_with_default",
                "request_field_with_no_default": "request_field_with_no_default",
                "json_field_with_default": {"key": "value"},
            }
        ]
    }

    identifier = response.json()["items"][0][model_identifier]

    response = client.get(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        model_identifier: identifier,
        "field_with_blank_true": "",
        "field_with_blank_true_and_default": "field_with_blank_true_and_default",
        "hidden_field_with_default": "Default",
        "request_field_with_default": "request_field_with_default",
        "request_field_with_no_default": "request_field_with_no_default",
        "json_field_with_default": {"key": "value"},
    }


@pytest.mark.django_db(transaction=True)
def test_model_with_default_create_list_get_with_unsupported_json_field(client_and_routebuilder, mocker):
    client, route_builder = client_and_routebuilder
    model_identifier, base_path = route_builder.model_identifier, route_builder.path_for_list_and_post

    response = client.post(
        base_path,
        json={
            "request_field_with_default": "request_field_with_default",
            "request_field_with_no_default": "request_field_with_no_default",
            "json_field_with_default": {},
        },
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        model_identifier: mocker.ANY,
        "field_with_blank_true": "",
        "hidden_field_with_default": "Default",
        "field_with_blank_true_and_default": "field_with_blank_true_and_default",
        "request_field_with_default": "request_field_with_default",
        "request_field_with_no_default": "request_field_with_no_default",
        "json_field_with_default": {
            "error": "JSONField not supported with value '{}', use projectx.common.fields.JSONDefaultField"
        },
    }

    response = client.get(base_path)
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "items": [
            {
                model_identifier: mocker.ANY,
                "field_with_blank_true": "",
                "field_with_blank_true_and_default": "field_with_blank_true_and_default",
                "hidden_field_with_default": "Default",
                "request_field_with_default": "request_field_with_default",
                "request_field_with_no_default": "request_field_with_no_default",
                "json_field_with_default": {
                    "error": "JSONField not supported with value '{}', use projectx.common.fields.JSONDefaultField"
                },
            }
        ]
    }

    identifier = response.json()["items"][0][model_identifier]

    response = client.get(f"{base_path}{identifier}/")
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        model_identifier: identifier,
        "field_with_blank_true": "",
        "field_with_blank_true_and_default": "field_with_blank_true_and_default",
        "hidden_field_with_default": "Default",
        "request_field_with_default": "request_field_with_default",
        "request_field_with_no_default": "request_field_with_no_default",
        "json_field_with_default": {
            "error": "JSONField not supported with value '{}', use projectx.common.fields.JSONDefaultField"
        },
    }
