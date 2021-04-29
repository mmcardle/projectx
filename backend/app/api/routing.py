from uuid import UUID

from fastapi import APIRouter

from users.models import User

# The API model for one object.
from .fastapi import RouteBuilder

router = APIRouter()

request_fields = ["email", "first_name", "last_name"]
response_fields = ["public_uuid", "email", "first_name", "last_name"]
config = {"identifier": "public_uuid", "identifier_class": UUID}

route_builder = RouteBuilder(User, request_fields, response_fields, config)

route_builder.add_all_routes_to_router(router)
