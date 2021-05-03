import logging
from typing import Callable, List, Optional
from urllib import parse

from django.db import models
from djantic import ModelSchema
from fastapi import Body, Depends, Header, HTTPException, Path
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from users.models import ApiKey, User

API_KEY_HEADER = Header(..., description="The user's API key.")


logger = logging.getLogger(__name__)


def check_api_key(x_api_key: str = API_KEY_HEADER) -> User:
    """
    Retrieve the user by the given API key.
    """
    api_keys = ApiKey.objects.filter(key=x_api_key)
    if api_keys.exists():
        return api_keys.first().user
    raise HTTPException(status_code=400, detail="X-API-Key header invalid.")


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
            return cls(**{field: getattr(instance, field) for field in fields})

    return SingleSchema


def schema_for_new_instance(django_model, SingleSchema, fields):  # pylint: disable=invalid-name
    class NewSchema(ModelSchema):
        class Config:  # pylint: disable=too-few-public-methods
            model = django_model
            include = fields

        def create_new(self, extra=None):
            """
            Create a new Django model instance.
            """
            data_fields = {field: getattr(self, field) for field in fields}
            if extra:
                data_fields.update(extra)
            return django_model.objects.create(**data_fields)

        def update(self, instance: django_model):
            """
            Update a Django model instance and return an SingleSchema instance.
            """
            for field in fields:
                current_field_value = getattr(self, field)
                setattr(instance, field, current_field_value)
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


class RouteBuilder:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        model: models.Model,
        request_fields: List[str],
        response_fields: List[str],
        read_only_fields: List[str],
        config: dict = None,
        owner_field: str = None,
        current_user_function: Optional[Callable] = None,
    ) -> None:
        self.model = model
        self.owner_field = owner_field

        self.config = config if config else {}

        self.instance_schema = schema_for_instance(model, response_fields + read_only_fields)

        fields_for_new = request_fields
        self.new_instance_schema = schema_for_new_instance(model, self.instance_schema, fields_for_new)
        self.multiple_instance_schema = schema_for_multiple_models(self.instance_schema)

        self.get_function = self.get_identifier_function()

        if current_user_function is None:
            self.current_user_function = check_api_key
        else:
            self.current_user_function = current_user_function

    @property
    def model_identifier_class(self):
        return self.config.get("identifier_class", str)

    @property
    def model_identifier(self):
        return self.config.get("identifier", "id")

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

    def check_ownership(self, instance, user):
        return user == getattr(instance, self.owner_field)

    def get_identifier_function(self):
        def func(
            identifier: self.model_identifier_class = Path(..., description=f"The identifier of the {self.name}."),
        ):
            """
            Retrieve the instance from the given model identifier.
            """
            instance = self.model.objects.filter(**{self.model_identifier: identifier}).first()
            if not instance:
                raise HTTPException(status_code=404, detail=f"Object {identifier} not found.")
            return instance

        return func

    def add_list_route_to_router(self, router):
        @router.get(
            self.path_for_list_and_post,
            summary=f"Retrieve a list of all the {self.name_plural}.",
            tags=[f"{self.name_plural}"],
            response_model=self.multiple_instance_schema,
            name=f"{self.name_lower_plural}-get",
        )
        def _get(user: User = Depends(self.current_user_function)) -> self.multiple_instance_schema:
            if self.owner_field:
                all_models = self.model.objects.filter(**{self.owner_field: user})
            else:
                all_models = self.model.objects.all()
            return self.multiple_instance_schema.from_qs(all_models)

        return _get

    def add_get_route_to_router(self, router):
        @router.get(
            self.path_for_identifer,
            summary=f"Get a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.instance_schema,
            name=f"{self.name_lower}-get",
        )
        def _get(
            instance: self.model = Depends(self.get_function),
            user: User = Depends(self.current_user_function),
        ) -> self.instance_schema:
            if self.owner_field and not self.check_ownership(instance, user):
                owner = getattr(instance, self.owner_field)
                logger.warning("User %s tried to get %s and is not the owner, owner is %s.", user, instance, owner)
                raise HTTPException(status_code=404, detail="Object not found.")
            return self.instance_schema.from_model(instance)

        return _get

    def add_create_route_to_router(self, router):
        @router.post(
            self.path_for_list_and_post,
            summary=f"Create a new {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.instance_schema,
            name=f"{self.name_lower_plural}-post",
        )
        def _post(
            api_instance: self.new_instance_schema, user: User = Depends(self.current_user_function)
        ) -> self.instance_schema:
            extra = {self.owner_field: user} if self.owner_field else None
            instance = api_instance.create_new(extra=extra)
            return self.instance_schema.from_model(instance)

        return _post

    def add_update_route_to_router(self, router):
        @router.put(
            self.path_for_identifer,
            summary=f"Update a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.instance_schema,
            name=f"{self.name_lower}-put",
        )
        def _put(
            instance: self.model = Depends(self.get_function),
            api_instance: self.new_instance_schema = Body(...),
            user: User = Depends(self.current_user_function),
        ) -> self.instance_schema:
            if self.owner_field and not self.check_ownership(instance, user):
                owner = getattr(instance, self.owner_field)
                logger.warning("User %s tried to update %s and is not the owner, owner is %s.", user, instance, owner)
                raise HTTPException(status_code=404, detail="Object not found.")
            return api_instance.update(instance)

        return _put

    def add_delete_route_to_router(self, router):
        @router.delete(
            self.path_for_identifer,
            summary=f"Delete a {self.name}.",
            tags=[f"{self.name_plural}"],
            response_model=self.instance_schema,
            name=f"{self.name_lower}-delete",
        )
        def _delete(
            instance: self.model = Depends(self.get_function), user: User = Depends(self.current_user_function)
        ) -> self.instance_schema:
            if self.owner_field and not self.check_ownership(instance, user):
                owner = getattr(instance, self.owner_field)
                logger.warning("User %s tried to update %s and is not the owner, owner is %s.", user, instance, owner)
                raise HTTPException(status_code=404, detail="Object not found.")
            api_instance = self.instance_schema.from_model(instance)
            instance.delete()
            return api_instance

        return _delete
