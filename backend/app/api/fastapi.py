from urllib import parse
from uuid import UUID
from typing import List

from django.db import models
from fastapi import Body, Depends, Header, HTTPException, Path
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic_django import ModelSchema


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
    user_uuid2: UUID = Path(..., description="The UUID of the user."),
    x_api_key: str = Header(...),
):
    """
    Retrieve the user from the given user UUID.
    """
    _ = check_api_key(x_api_key)
    instance = User.objects.filter(public_uuid=user_uuid2).first()
    if not instance:
        raise HTTPException(status_code=404, detail=f"Object {user_uuid2} not found.")
    return instance


class RouteBuilder:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        django_model: models.Model,
        django_model_identifier: str,
        config: dict = None,
    ) -> None:
        self.django_model = django_model
        self.django_model_identifier = django_model_identifier
        self.config = config if config else {}
        self.name = self.config.get("name", self.django_model.__name__)
        self.name_plural = f"{self.name}s"
        self.name_lower = self.config.get("name", self.django_model.__name__).lower()
        self.name_lower_plural = f"{self.name_lower}s"
        self.path_prefix = f"/{parse.quote(self.name_lower_plural)}/"
        self.path_for_list_and_post = self.path_prefix
        self.path_for_identifer = self.path_prefix + "{" + django_model_identifier + "}/"

        class NewSchema(ModelSchema):
            class Config:  # pylint: disable=too-few-public-methods
                model = self.django_model
                include = ["email", "first_name", "last_name"]

            def create_new(self):
                """
                Create a new Django model instance.
                """
                return django_model.create_new(
                    email=self.email,
                    first_name=self.first_name,
                    last_name=self.last_name,
                )

            def update(self, instance: django_model):
                """
                Update a Django model instance and return an SingleSchema instance.
                """
                instance.email = self.email or instance.email
                instance.first_name = self.first_name or instance.first_name
                instance.last_name = self.last_name or instance.last_name
                instance.save()
                return SingleSchema.from_model(instance)

        class SingleSchema(ModelSchema):
            class Config:  # pylint: disable=too-few-public-methods
                model = self.django_model
                include = ["public_uuid", "email", "first_name", "last_name"]

            @classmethod
            def from_model(cls, instance: self.django_model):
                """
                Convert a Django model instance to an SingleSchema instance.
                """
                return cls(
                    public_uuid=instance.public_uuid,
                    email=instance.email,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                )

        class MultipleSchema(BaseModel):  # pylint: disable=too-few-public-methods
            items: List[SingleSchema]

            @classmethod
            def from_qs(cls, qs):
                """
                Convert a Django queryset to a MultipleSchema instance.
                """
                return cls(items=[SingleSchema.from_model(i) for i in qs])

        self.fast_api_model = NewSchema
        self.fast_api_single_model = SingleSchema
        self.fast_api_multiple_model = MultipleSchema

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
