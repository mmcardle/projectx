import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from test_app import models

from api.fastapi import (
    InvalidAuthenticationException,
    InvalidFieldsException,
    RouteBuilder,
)
from api.wsgi import application

client = TestClient(application)


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(models.TestModel)
    route_builder.add_all_routes(router)
    assert len(router.routes) == 5


def test_route_builder_owner_field_but_no_auth():
    with pytest.raises(InvalidAuthenticationException) as invalid_ex:
        RouteBuilder(models.TestModel, owner_field="user_field")

    assert str(invalid_ex.value) == "If you specify an owner field, you must have set the authentication function."


def test_route_builder_invalid_fields():
    with pytest.raises(InvalidFieldsException) as invalid_ex:
        RouteBuilder(models.TestModel, request_fields=["invalid"])

    assert str(invalid_ex.value) == "['invalid'] not in ['config', 'created', 'id', 'last_updated', 'name', 'uuid']"
