from common.validation import create_payload_decorator

from . import validation


def activate_check_payload(func):
    return create_payload_decorator(
        func, validation.ActivateCheckSchema, error_msg="Invalid activate check data"
    )


def activate_payload(func):
    return create_payload_decorator(
        func, validation.ActivateSchema, error_msg="Invalid activate data"
    )
