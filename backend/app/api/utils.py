from urllib import parse
from uuid import UUID

from django.db import models
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Path
from pydantic import BaseModel  # pylint: disable=no-name-in-module

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


class RouteBuilder:
    def __init__(
        self,
        django_model: models.Model,
        django_model_identifier: str,
        fast_api_model: BaseModel,
        fast_api_single_model: BaseModel,
        fast_api_multiple_model: BaseModel,
        config: dict = None,
    ) -> None:
        self.django_model = django_model
        self.django_model_identifier = django_model_identifier
        self.fast_api_model = fast_api_model
        self.fast_api_single_model = fast_api_single_model
        self.fast_api_multiple_model = fast_api_multiple_model
        self.config = config if config else {}
        self.name = config.get("name", self.django_model.__name__)
        self.name_plural = f"{self.name}s"
        self.name_lower = config.get("name", self.django_model.__name__).lower()
        self.name_lower_plural = f"{self.name_lower}s"
        self.path_prefix = f"/{parse.quote(self.name_lower_plural)}/"
        self.path_for_list_and_post = self.path_prefix
        self.path_for_identifer = self.path_prefix + "{" + django_model_identifier + "}/"

    def add_list_route_to_router(self, router):
        @router.get(
            self.path_for_list_and_post,
            summary=f"Retrieve a list of all the {self.name_plural}.",
            tags=[f"{self.name_plural}"],
            response_model=self.fast_api_multiple_model,
            name=f"{self.name_lower_plural}-get",
        )
        def _get(_: User = Depends(check_api_key)) -> self.fast_api_multiple_model:
            all_models = self.django_model.objects.all()
            return self.fast_api_multiple_model.from_qs(all_models)

        return _get

    def add_get_route_to_router(self, router, get_function):
        @router.get(
            self.path_for_identifer,
            summary=f"Get a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.fast_api_single_model,
            name=f"{self.name_lower}-get",
        )
        def _get(
            instance: self.django_model = Depends(get_function),
            _: User = Depends(check_api_key),
        ) -> self.fast_api_single_model:
            return self.fast_api_single_model.from_model(instance)

        return _get

    def add_create_route_to_router(self, router):
        @router.post(
            self.path_for_list_and_post,
            summary=f"Create a new {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.fast_api_single_model,
            name=f"{self.name_lower_plural}-post",
        )
        def _post(api_instance: self.fast_api_model, _: User = Depends(check_api_key)) -> self.fast_api_single_model:
            instance = api_instance.create_new()
            return self.fast_api_single_model.from_model(instance)

        return _post

    def add_update_route_to_router(self, router, get_function):
        @router.put(
            self.path_for_identifer,
            summary=f"Update a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.fast_api_single_model,
            name=f"{self.name_lower}-put",
        )
        def _put(
            instance: self.django_model = Depends(get_function),
            api_instance: self.fast_api_model = Body(...),
            _: User = Depends(check_api_key),
        ) -> self.fast_api_single_model:
            return api_instance.update(instance)

        return _put

    def add_delete_route_to_router(self, router, get_function):
        @router.delete(
            self.path_for_identifer,
            # "/users/{user_uuid}/",
            summary=f"Delete a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.fast_api_single_model,
            name=f"{self.name_lower}-delete",
        )
        def _delete(
            instance: self.django_model = Depends(get_function), _: User = Depends(check_api_key)
        ) -> self.fast_api_single_model:
            api_instance = self.fast_api_single_model.from_model(instance)
            instance.delete()
            return api_instance

        return _delete
