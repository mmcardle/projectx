import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import RouteBuilder
from api.wsgi import application
from users.models import ApiKey, User

client = TestClient(application)


API_KEY = "api_key"


@pytest.mark.django_db(transaction=True)
@pytest.fixture(name="api_key_user")
def api_key_user_fixture():
    user = User.objects.create_user(email="apikeyuser@tempurl.com", first_name="API", last_name="Test User")
    return ApiKey.objects.create(user=user, key=API_KEY)


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(User, [], [], [])
    route_builder.add_list_route_to_router(router)
    route_builder.add_get_route_to_router(router)
    route_builder.add_create_route_to_router(router)
    route_builder.add_update_route_to_router(router)
    route_builder.add_delete_route_to_router(router)
    assert len(router.routes) == 5
