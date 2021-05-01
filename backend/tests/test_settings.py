from projectx.settings import *  # noqa

# Override any settings required for tests here
INSTALLED_APPS.append(
    "test_app.app.TestAppConfig",
)
