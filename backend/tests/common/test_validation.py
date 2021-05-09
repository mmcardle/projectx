# pylint: disable=invalid-name
import json
import pytest

from marshmallow import Schema, fields

from common import validation


class DummySchema(Schema):
    email = fields.Email(required=True)


def test_create_payload_decorator_ok(mocker):
    func = mocker.Mock(__name__="name")
    decorator = validation.create_payload_decorator(func, DummySchema)

    data = {"email": "none@none.com"}

    request = mocker.Mock(body=json.dumps(data))
    result = decorator(request)

    assert result == func.return_value
    assert func.mock_calls == [mocker.call(request)]


def test_create_payload_decorator_bad_data(mocker):

    JsonResponse = mocker.patch("common.validation.JsonResponse")

    func = mocker.Mock(__name__="name")
    decorator = validation.create_payload_decorator(func, DummySchema)

    request = mocker.Mock(body=json.dumps({}))
    result = decorator(request)

    assert func.mock_calls == []
    assert JsonResponse.mock_calls == [
        mocker.call(
            {
                "error": "Invalid Data",
                "errors": {"email": ["Missing data for required field."]},
            },
            status=400,
        )
    ]
    assert result == JsonResponse.return_value


def test_validation_load_data_from_schema_no_data():
    with pytest.raises(validation.SchemaError):
        validation.load_data_from_schema(DummySchema(), {})


def test_validation_load_data_from_schema_OK():
    data = {"email": "none@none.com"}
    assert validation.load_data_from_schema(DummySchema(), data) == data


def test_check_schema_payload_OK(mocker):
    user = mocker.Mock()
    payload = {"email": "none@none.com"}
    assert validation.check_schema_payload(user, payload, DummySchema) == (True, payload)


def test_check_schema_payload_no_data(mocker):
    user = mocker.Mock()
    payload = {}
    assert validation.check_schema_payload(user, payload, DummySchema) == (
        False,
        {"email": ["Missing data for required field."]},
    )
