from uuid import UUID

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from test_app.models import TestModelWithJWT

from api.fastapi import RouteBuilder
from api.wsgi import application as app
from users.app import get_user_authentication
from users.models import User

BASE_PATH = "/testmodelwithjwts/"
JWT_PATH = "/api/auth/token/"
JWT_USER_PASSWORD = "jwtpassword"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="client")
def get_client():
    router = APIRouter()
    authentication, _ = get_user_authentication()
    route_builder = RouteBuilder(
        TestModelWithJWT,
        request_fields=["name"],
        response_fields=["name", "uuid"],
        config={"identifier": "uuid", "identifier_class": UUID},
        authentication=authentication,
    )

    route_builder.add_all_routes(router)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="jwt_user")
def jwt_user_fixture():
    return User.objects.create_user(
        email="jwt_user@tempurl.com", first_name="JWT", last_name="Test User", password=JWT_USER_PASSWORD
    )


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithjwt_create_get_and_delete(client, jwt_user, mocker):

    response = client.post(
        JWT_PATH,
        data={"username": jwt_user.username, "password": JWT_USER_PASSWORD},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }

    access_token = response.json()["access_token"]

    response = client.post(
        BASE_PATH,
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "name"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    uuid = response.json()["uuid"]

    response = client.get(
        f"{BASE_PATH}{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    response = client.delete(
        f"{BASE_PATH}{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.content.decode("utf-8")
    assert response.json() == {
        "name": "name",
        "uuid": mocker.ANY,
    }

    response = client.get(
        f"{BASE_PATH}{uuid}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404, response.content.decode("utf-8")
    assert response.json() == {"detail": f"Object {uuid} not found."}
