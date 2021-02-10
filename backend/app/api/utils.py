from uuid import UUID

from fastapi import Header, HTTPException, Path

from users.models import User

# This is to avoid typing it once every object.
API_KEY_HEADER = Header(..., description="The user's API key.")


def check_api_key(x_api_key: str = API_KEY_HEADER) -> User:
    """
    Retrieve the user by the given API key.
    """
    user = User.objects.filter().first()
    if x_api_key != "api_key":
        raise HTTPException(status_code=400, detail="X-API-Key header invalid.")
    return user


def get_user(
    user_uuid: UUID = Path(..., description="The UUID of the user."),
    x_api_key: str = Header(...),
):
    """
    Retrieve the user from the given user UUID.
    """
    _ = check_api_key(x_api_key)
    instance = User.objects.filter(public_uuid=user_uuid).first()
    if not instance:
        raise HTTPException(status_code=404, detail=f"Object {user_uuid} not found.")
    return instance
