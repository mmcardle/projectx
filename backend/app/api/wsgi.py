"""
WSGI config for Project3.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/
"""

import os
import sys

import django
from fastapi import FastAPI

sys.path.append("app/")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectx.settings")  # noqa
django.setup()  # noqa

from .routing import router  # pylint: disable=wrong-import-position

application = FastAPI(
    title="ProjectX",
    description="ProjectX Demo",
    version="0.0.1",
    docs_url="/api/docs",
    openapi_url="/api/v1/openapi.json"
)

application.include_router(router, prefix="/api")
