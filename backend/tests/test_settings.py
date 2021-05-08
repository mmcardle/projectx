from projectx.settings import *  # noqa

# Override any settings required for tests here
INSTALLED_APPS.extend(
    [
        "test_app_with_jwt_user.app.TestAppWithJWTUserConfig",
        "test_app_with_api_key.app.TestAppWithAPIKeyConfig",
        "test_app_with_owner.app.TestAppWithOwnerConfig",
        "test_app_with_no_auth.app.TestAppWithNoAuthenticationConfig",
        "test_app_with_related_model.app.TestAppWithRelatedModelConfig",
    ]
)

LOGGING = {}
