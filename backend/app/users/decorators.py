from common.validation import create_payload_decorator

from users import validation


def activate_payload(func):
    return create_payload_decorator(func, validation.ActivateSchema, error_msg="Invalid activate data")


def register_payload(func):
    return create_payload_decorator(func, validation.RegisterSchema, error_msg="Invalid register data")


def reset_password_payload(func):
    return create_payload_decorator(func, validation.ResetPasswordSchema, error_msg="Invalid reset password data")


def reset_password_check_payload(func):
    return create_payload_decorator(
        func, validation.ResetPasswordCheckSchema, error_msg="Invalid reset password check data"
    )


def reset_password_complete_payload(func):
    return create_payload_decorator(
        func, validation.ResetPasswordCompleteSchema, error_msg="Invalid reset password complete data"
    )


def change_password_payload(func):
    return create_payload_decorator(func, validation.ChangePasswordSchema, error_msg="Invalid change password data")


def change_details_payload(func):
    return create_payload_decorator(func, validation.ChangeDetailsSchema, error_msg="Invalid change details data")
