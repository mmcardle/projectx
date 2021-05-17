# pylint: disable=unused-wildcard-import disable=wildcard-import
from projectx.settings import *

# Override any settings required for tests here
INSTALLED_APPS.append("test_app")

LOGGING = {}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
