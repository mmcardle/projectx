import pytest
from test_app.models import (
    BadJSONModelWithDefault,
    BadJSONModelWithNoDefault,
    GoodJSONModel,
)

from projectx.api.fastapi import RouteBuilder, UnSupportedFieldException


def test_bad_json_field_with_default():
    with pytest.raises(UnSupportedFieldException) as exception:
        RouteBuilder(BadJSONModelWithDefault)

    assert str(exception.value) == (
        "Field test_app.BadJSONModelWithDefault.data with default '{}' "
        "is not supported, try using 'projectx.common.fields.JSONDefaultField'"
    )


def test_bad_json_field_with_no_default():
    with pytest.raises(UnSupportedFieldException) as exception:
        RouteBuilder(BadJSONModelWithNoDefault)

    assert str(exception.value) == (
        "Field test_app.BadJSONModelWithNoDefault.data with no default "
        "is not supported, try using 'projectx.common.fields.JSONDefaultField'"
    )


def test_good_json_field():
    assert RouteBuilder(GoodJSONModel)
