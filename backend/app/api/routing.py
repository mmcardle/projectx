from fastapi import APIRouter, Body, Depends

from users.models import User

# The API model for one object.
from .fastapi import APIUser, MultipleAPIUsers, SingleAPIUser
from .utils import get_user, add_list_route, add_get_route, add_create_route, add_update_route, add_delete_route

router = APIRouter()

config = {"name": "User"}

add_list_route(router, User, MultipleAPIUsers, config=config)
add_get_route(router, User, SingleAPIUser, get_user, config=config)
add_create_route(router, User, APIUser, SingleAPIUser, config=config)
add_update_route(router, User, SingleAPIUser, get_user, config=config)
add_delete_route(router, User, SingleAPIUser, get_user, config=config)
