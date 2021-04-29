from typing import List
from urllib import parse
from uuid import UUID

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


def schema_for_instance(django_model, fields):
    class SingleSchema(ModelSchema):  # pylint: disable=too-few-public-methods
        class Config:  # pylint: disable=too-few-public-methods
            model = django_model
            include = fields

        @classmethod
        def from_model(cls, instance: django_model):
            """
            Convert a Django model instance to an SingleSchema instance.
            """
            return cls(
                public_uuid=instance.public_uuid,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
            )

    return SingleSchema


def schema_for_new_model(django_model, SingleSchema, fields):  # pylint: disable=invalid-name
    class NewSchema(ModelSchema):
        class Config:  # pylint: disable=too-few-public-methods
            model = django_model
            include = fields

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

    return NewSchema


def schema_for_multiple_models(SingleSchema):  # pylint: disable=invalid-name
    class MultipleSchema(BaseModel):  # pylint: disable=too-few-public-methods
        items: List[SingleSchema]

        @classmethod
        def from_qs(cls, qs):
            """
            Convert a Django queryset to a MultipleSchema instance.
            """
            return cls(items=[SingleSchema.from_model(i) for i in qs])

    return MultipleSchema


class RouteBuilder:
    def __init__(
        self,
        model: models.Model,
        request_fields: List[str],
        response_fields: List[str],
        config: dict = None,
    ) -> None:
        self.model = model
        self.config = config if config else {}

        self.new_instance_schema = schema_for_instance(model, response_fields)
        self.multiple_instance_schema = schema_for_multiple_models(self.new_instance_schema)
        self.instance_schema = schema_for_new_model(model, self.new_instance_schema, request_fields)

        self.get_function = self.get_identifier_function()

    def get_identifier_function(self):
        def _inner(
            identifier: UUID = Path(..., description=f"The identifier of the {self.name}."),
            x_api_key: str = Header(...),
        ):
            """
            Retrieve the instance from the given model identifier.
            """
            _ = check_api_key(x_api_key)
            instance = self.model.objects.filter(public_uuid=identifier).first()
            if not instance:
                raise HTTPException(status_code=404, detail=f"Object {identifier} not found.")
            return instance

        return _inner

    @property
    def name(self):
        return self.config.get("name", self.model.__name__)

    @property
    def name_plural(self):
        return f"{self.name}s"

    @property
    def name_lower(self):
        return self.config.get("name", self.model.__name__).lower()

    @property
    def name_lower_plural(self):
        return f"{self.name_lower}s"

    @property
    def path_prefix(self):
        return f"/{parse.quote(self.name_lower_plural)}/"

    @property
    def path_for_list_and_post(self):
        return self.path_prefix

    @property
    def path_for_identifer(self):
        return self.path_prefix + "{identifier}/"

    def add_list_route_to_router(self, router):
        @router.get(
            self.path_for_list_and_post,
            summary=f"Retrieve a list of all the {self.name_plural}.",
            tags=[f"{self.name_plural}"],
            response_model=self.multiple_instance_schema,
            name=f"{self.name_lower_plural}-get",
        )
        def _get(_: User = Depends(check_api_key)) -> self.multiple_instance_schema:
            all_models = self.model.objects.all()
            return self.multiple_instance_schema.from_qs(all_models)

        return _get

    def add_get_route_to_router(self, router):
        @router.get(
            self.path_for_identifer,
            summary=f"Get a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.new_instance_schema,
            name=f"{self.name_lower}-get",
        )
        def _get(
            instance: self.model = Depends(self.get_function),
            _: User = Depends(check_api_key),
        ) -> self.new_instance_schema:
            return self.new_instance_schema.from_model(instance)

        return _get

    def add_create_route_to_router(self, router):
        @router.post(
            self.path_for_list_and_post,
            summary=f"Create a new {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.new_instance_schema,
            name=f"{self.name_lower_plural}-post",
        )
        def _post(api_instance: self.instance_schema, _: User = Depends(check_api_key)) -> self.new_instance_schema:
            instance = api_instance.create_new()
            return self.new_instance_schema.from_model(instance)

        return _post

    def add_update_route_to_router(self, router):
        @router.put(
            self.path_for_identifer,
            summary=f"Update a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.new_instance_schema,
            name=f"{self.name_lower}-put",
        )
        def _put(
            instance: self.model = Depends(self.get_function),
            api_instance: self.instance_schema = Body(...),
            _: User = Depends(check_api_key),
        ) -> self.new_instance_schema:
            return api_instance.update(instance)

        return _put

    def add_delete_route_to_router(self, router):
        @router.delete(
            self.path_for_identifer,
            summary=f"Delete a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.new_instance_schema,
            name=f"{self.name_lower}-delete",
        )
        def _delete(
            instance: self.model = Depends(self.get_function), _: User = Depends(check_api_key)
        ) -> self.new_instance_schema:
            api_instance = self.new_instance_schema.from_model(instance)
            instance.delete()
            return api_instance

        return _delete
