import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from api.fastapi import InvalidFieldsException, RouteBuilder
from api.wsgi import application
from test_app1 import models

client = TestClient(application)


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(models.TestModel, [], [], [])
    route_builder.add_list_route_to_router(router)
    route_builder.add_get_route_to_router(router)
    route_builder.add_create_route_to_router(router)
    route_builder.add_update_route_to_router(router)
    route_builder.add_delete_route_to_router(router)
    assert len(router.routes) == 5


def test_route_builder_invalid_fields():
    with pytest.raises(InvalidFieldsException) as invalid_ex:
        RouteBuilder(models.TestModel, ["invalid"], [], [])

    assert str(invalid_ex.value) == "{'invalid'} not in ['id', 'uuid', 'name', 'last_updated', 'created', 'config']"
