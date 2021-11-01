import os

from django.apps import apps
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectx.settings")
apps.populate(settings.INSTALLED_APPS)

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware

from projectx.api.routing import router
from projectx.channels import application as channels_application


def get_application() -> FastAPI:
    app = FastAPI(
        title="ProjectX",
        description="ProjectX Demo",
        version="0.0.1",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/v1/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    app.mount("/", channels_application)

    return app


application = get_application()
