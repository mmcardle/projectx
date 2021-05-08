import pytest
from fastapi.testclient import TestClient

from api.wsgi import application
from users.models import User

client = TestClient(application)

BASE_PATH = "/api/testmodelwithjwts/"
JWT_PATH = "/api/auth/token/"
JWT_USER_PASSWORD = "jwtpassword"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="jwt_user")
def jwt_user_fixture():
    return User.objects.create_user(
        email="jwt_user@tempurl.com", first_name="JWT", last_name="Test User", password=JWT_USER_PASSWORD
    )


@pytest.mark.django_db(transaction=True)
def test_testapp_testmodelwithjwt_create_get_and_delete(jwt_user, mocker):

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
