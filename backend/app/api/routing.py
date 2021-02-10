from fastapi import APIRouter, Body, Depends

from users.models import User

# The API model for one object.
from .models import APIUser, MultipleAPIUsers, SingleAPIUser
from .utils import check_api_key, get_user

router = APIRouter()


@router.get(
    "/users/",
    summary="Retrieve a list of all the users.",
    tags=["users"],
    response_model=MultipleAPIUsers,
    name="users-get",
)
def users_get(_: User = Depends(check_api_key)) -> MultipleAPIUsers:
    models = User.objects.all()
    return MultipleAPIUsers.from_qs(models)


@router.post(
    "/users/",
    summary="Create a new user.",
    tags=["users"],
    response_model=SingleAPIUser,
    name="users-post",
)
def user_post(
    api_user: APIUser,
    _: User = Depends(check_api_key)
) -> SingleAPIUser:
    user = api_user.new_user()
    return SingleAPIUser.from_model(user)


@router.get(
    "/users/{user_uuid}/",
    summary="Get a user.",
    tags=["users"],
    response_model=SingleAPIUser,
    name="user-get",
)
def user_get(
    user: User = Depends(get_user),
    _: User = Depends(check_api_key),
) -> SingleAPIUser:
    return SingleAPIUser.from_model(user)


@router.put(
    "/users/{user_uuid}/",
    summary="Update a user.",
    tags=["users"],
    response_model=SingleAPIUser,
    name="user-put",
)
def user_put(
    user: User = Depends(get_user),
    api_user: APIUser = Body(...),
    _: User = Depends(check_api_key),
) -> SingleAPIUser:
    return api_user.update_user(user)


@router.delete(
    "/users/{user_uuid}/",
    summary="Delete a user.",
    tags=["users"],
    response_model=SingleAPIUser,
    name="user-delete",
)
def user_delete(
    user: User = Depends(get_user),
    _: User = Depends(check_api_key)
) -> SingleAPIUser:
    api_user = SingleAPIUser.from_model(user)
    user.delete()
    return api_user
