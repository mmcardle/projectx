import json
import logging

from django.http import JsonResponse
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


class SchemaError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


def create_payload_decorator(function, schema_class, error_msg="Invalid Data"):
    def wrap(request, *args, **kwargs):
        payload = json.loads(request.body)
        user = request.user
        check_ok, check_result = check_schema_payload(user, payload, schema_class)

        if check_ok:
            request.validated_data = check_result
            return function(request, *args, **kwargs)

        logger.error("%s: %s", error_msg, check_result)
        return JsonResponse(
            {
                "error": error_msg,
                "errors": check_result,
            },
            status=400,
        )

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def load_data_from_schema(schema, data):
    try:
        validated_data = schema.load(data=data)
    except ValidationError as validation_error:
        schema_name = schema.__class__.__name__
        error = f"Error validating {schema_name}: {validation_error.messages}"
        raise SchemaError(error, validation_error.messages) from validation_error
    return validated_data


def check_schema_payload(user, payload, schema_class):
    schema = schema_class()
    schema.context = {"user": user}
    try:
        data = load_data_from_schema(schema, payload)
        return True, data
    except SchemaError as schema_error:
        return False, schema_error.errors
