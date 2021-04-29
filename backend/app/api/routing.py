from fastapi import APIRouter

from users.models import User

# The API model for one object.
from .fastapi import RouteBuilder, get_user

router = APIRouter()

route_builder = RouteBuilder(User, "user_uuid2")

route_builder.add_list_route_to_router(router)
route_builder.add_get_route_to_router(router, get_user)
route_builder.add_create_route_to_router(router)
route_builder.add_update_route_to_router(router, get_user)
route_builder.add_delete_route_to_router(router, get_user)
