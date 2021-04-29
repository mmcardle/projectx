from fastapi import APIRouter

from users.models import User

# The API model for one object.
from .fastapi import RouteBuilder

router = APIRouter()

request_fields = ["email", "first_name", "last_name"]
response_fields = ["public_uuid", "email", "first_name", "last_name"]
route_builder = RouteBuilder(User, request_fields, response_fields)

route_builder.add_list_route_to_router(router)
route_builder.add_get_route_to_router(router)
route_builder.add_create_route_to_router(router)
route_builder.add_update_route_to_router(router)
route_builder.add_delete_route_to_router(router)
