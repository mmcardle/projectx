from fastapi import APIRouter, Body, Depends

from users.models import User

# The API model for one object.
from .models import FastAPIUser, MultipleFastAPIUsers, SingleFastAPIUser
from .utils import check_api_key, get_user

router = APIRouter()


@router.get(
    "/users/",
    summary="Retrieve a list of all the users.",
    tags=["users"],
    response_model=MultipleFastAPIUsers,
    name="users-get",
)
def users_get(_: User = Depends(check_api_key)) -> MultipleFastAPIUsers:
    models = User.objects.all()
    return MultipleFastAPIUsers.from_qs(models)


@router.post(
    "/user/",
    summary="Create a new user.",
    tags=["users"],
    response_model=SingleFastAPIUser,
    name="users-post",
)
def user_post(
    fast_api_user: FastAPIUser,
    _: User = Depends(check_api_key)
) -> SingleFastAPIUser:
    """
    Create a new user.
    """
    user = fast_api_user.new_user()
    return SingleFastAPIUser.from_model(user)


@router.put(
    "/user/{user_uuid}/",
    summary="Update a user.",
    tags=["users"],
    response_model=SingleFastAPIUser,
    name="user-put",
)
def user_put(
    user: User = Depends(get_user),
    fast_api_user: FastAPIUser = Body(...),
    _: User = Depends(check_api_key),
) -> SingleFastAPIUser:
    """
    Update a user.
    """
    return fast_api_user.update_user(user)


@router.delete(
    "/user/{user_uuid}/",
    summary="Delete a user.",
    tags=["users"],
    response_model=SingleFastAPIUser,
    name="user-delete",
)
def user_delete(
    user: User = Depends(get_user),
    _: User = Depends(check_api_key)
) -> SingleFastAPIUser:
    """
    Delete a user.
    """
    model_user = SingleFastAPIUser.from_model(user)
    user.delete()
    return model_user
