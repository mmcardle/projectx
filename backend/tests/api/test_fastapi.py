import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from test_app import models

from projectx.api.asgi import application
from projectx.api.fastapi import (
    InvalidAuthenticationException,
    InvalidFieldsException,
    InvalidIdentifierException,
    RouteBuilder,
)

client = TestClient(application)


def test_route_builder_adds_routes():
    router = APIRouter()
    route_builder = RouteBuilder(models.SimpleModel)
    route_builder.add_all_routes(router)
    assert len(router.routes) == 6
    assert router.routes[0].path == "/simplemodels/"
    assert router.routes[1].path == "/simplemodels/{identifier}/"
    assert router.routes[2].path == "/simplemodels/"
    assert router.routes[3].path == "/simplemodels/{identifier}/"
    assert router.routes[4].path == "/simplemodels/{identifier}/"
    assert router.routes[5].path == "/simplemodels/{identifier}/"
    assert router.routes[0].methods == {"GET"}
    assert router.routes[1].methods == {"GET"}
    assert router.routes[2].methods == {"POST"}
    assert router.routes[3].methods == {"PUT"}
    assert router.routes[4].methods == {"PATCH"}
    assert router.routes[5].methods == {"DELETE"}


@pytest.mark.django_db(transaction=True)
def test_route_builder_get_identifier_function():

    simple_model = models.SimpleModel.objects.create(name="SimpleModel")

    route_builder = RouteBuilder(models.SimpleModel)
    identifier_function = route_builder.get_identifier_function()

    assert identifier_function(simple_model.id) == simple_model


def test_route_builder_with_owner_removes_owner_field():
    router = APIRouter()
    route_builder = RouteBuilder(models.SimpleModelWithOwner, owner_field="owner", authentication=lambda: None)
    route_builder.add_all_routes(router)
    assert "title" in route_builder.new_instance_schema.schema().keys()
    assert "owner" not in route_builder.new_instance_schema.schema().keys()
    assert "title" in route_builder.instance_schema.schema().keys()
    assert "owner" not in route_builder.instance_schema.schema().keys()


def test_route_builder_bad_identifier_field():
    with pytest.raises(InvalidIdentifierException) as invalid_ex:
        RouteBuilder(models.SimpleModel, config={"identifier": "BAD_FIELD"})

    assert str(invalid_ex.value) == "BAD_FIELD not in ['id', 'uuid', 'name', 'last_updated', 'created', 'config']."


def test_route_builder_owner_field_but_no_auth():
    with pytest.raises(InvalidAuthenticationException) as invalid_ex:
        RouteBuilder(models.SimpleModel, owner_field="user_field")

    assert str(invalid_ex.value) == "If you specify an owner field, you must have set the authentication function."


def test_route_builder_invalid_fields():
    with pytest.raises(InvalidFieldsException) as invalid_ex:
        RouteBuilder(models.SimpleModel, request_fields=["invalid"])

    assert str(invalid_ex.value) == "['invalid'] not in ['config', 'created', 'id', 'last_updated', 'name', 'uuid']"
