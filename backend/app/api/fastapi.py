import logging
from collections import defaultdict
from typing import Callable, List, Optional
from urllib import parse

from django.db import models
from django.db.models import Q
from djantic import ModelSchema
from fastapi import Body, Depends, Header, HTTPException, Path
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from users.models import ApiKey, User

API_KEY_HEADER = Header(..., description="The user's API key.")


logger = logging.getLogger(__name__)


class RouteBuilderException(Exception):
    pass


class InvalidAuthenticationException(RouteBuilderException):
    pass


class InvalidIdentifierException(RouteBuilderException):
    pass


class InvalidFieldsException(RouteBuilderException):
    pass


class InvalidForeignKeyException(RouteBuilderException):
    pass


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
            title = f"New{django_model.__name__}"
            model = django_model
            include = fields

        @classmethod
        def from_model(cls, instance: django_model):
            """
            Convert a Django model instance to an SingleSchema instance.
            """
            field_data = {}
            for field in fields:
                django_field = django_model._meta.get_field(field)
                if django_field.is_relation:
                    if django_field.many_to_one:
                        related_field = getattr(instance, field)
                        field_data[field] = related_field.pk
                    elif django_field.many_to_many:
                        pk_name = django_field.related_model._meta.pk.name
                        field_data[field] = [{pk_name: related.pk} for related in getattr(instance, field).all()]
                    else:
                        pk_name = django_field.related_model._meta.pk.name
                        field_data[field] = [
                            {pk_name: related.pk}
                            for related in django_field.related_model.objects.filter(pk=instance.pk)
                        ]
                else:
                    field_data[field] = getattr(instance, field)
            return cls(**field_data)

    return type(f"{django_model.__name__}", (SingleSchema,), {})


def schema_for_new_instance(django_model, SingleSchema, fields):  # pylint: disable=invalid-name
    class NewSchema(ModelSchema):
        class Config:  # pylint: disable=too-few-public-methods
            title = f"{django_model.__name__}"
            model = django_model
            include = fields

        def create_new(self, extra=None):
            """
            Create a new Django model instance.
            """
            field_data = {}
            many_to_many_fields = defaultdict(list)
            for field in fields:
                django_field = django_model._meta.get_field(field)
                if django_field.is_relation:
                    related_model = django_field.related_model
                    if django_field.many_to_many:
                        for related_data in getattr(self, field):
                            identifier = related_data[related_model._meta.pk.name]
                            related_object = related_model.objects.get(pk=identifier)
                            many_to_many_fields[field].append(related_object)
                    else:
                        field_data[field] = related_model.objects.get(pk=getattr(self, field))
                else:
                    field_data[field] = getattr(self, field)

            if extra:
                field_data.update(extra)

            new_object = django_model.objects.create(**field_data)

            for many_to_many_field in many_to_many_fields:
                ref_field = getattr(new_object, many_to_many_field)
                for related_value in many_to_many_fields[many_to_many_field]:
                    ref_field.add(related_value)

            return new_object

        def update(self, instance: django_model):
            """
            Update a Django model instance and return an SingleSchema instance.
            """
            many_to_many_fields = defaultdict(list)
            for field in fields:
                django_field = django_model._meta.get_field(field)
                if django_field.is_relation:
                    related_model = django_field.related_model
                    if django_field.many_to_many:
                        for related_data in getattr(self, field):
                            identifier = related_data[related_model._meta.pk.name]
                            related_object = related_model.objects.get(pk=identifier)
                            many_to_many_fields[field].append(related_object)
                    else:
                        current_field_value = related_model.objects.get(pk=getattr(self, field))
                        setattr(instance, field, current_field_value)
                else:
                    current_field_value = getattr(self, field)
                    setattr(instance, field, current_field_value)

            instance.save()

            for many_to_many_field in many_to_many_fields:
                ref_field = getattr(instance, many_to_many_field)
                ref_field.clear()
                for related_value in many_to_many_fields[many_to_many_field]:
                    ref_field.add(related_value)

            return SingleSchema.from_model(instance)

    return type(f"New{django_model.__name__}", (NewSchema,), {})


def schema_for_multiple_models(django_model, SingleSchema):  # pylint: disable=invalid-name
    class MultipleSchema(BaseModel):  # pylint: disable=too-few-public-methods
        items: List[SingleSchema]

        class Config:  # pylint: disable=too-few-public-methods
            title = f"{django_model.__name__}List"

        @classmethod
        def from_qs(cls, qs):
            """
            Convert a Django queryset to a MultipleSchema instance.
            """
            return cls(items=[SingleSchema.from_model(i) for i in qs])

    return type(f"{django_model.__name__}List", (MultipleSchema,), {})


class RouteBuilder:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        model: models.Model,
        config: dict = None,
        request_fields: Optional[List[str]] = None,
        response_fields: Optional[List[str]] = None,
        owner_field: str = None,
        query_filter: Callable[[User], Q] = None,
        authentication: Optional[Callable] = None,
    ) -> None:
        self.model = model
        self.owner_field = owner_field
        self.query_filter = query_filter

        if owner_field and not authentication:
            raise InvalidAuthenticationException(
                "If you specify an owner field, you must have set the authentication function."
            )

        self.config = config if config else {}

        model_fields_names = [field.name for field in self.model._meta.get_fields()]

        if self.model_identifier not in model_fields_names:
            raise InvalidIdentifierException(f"{self.model_identifier} not in {model_fields_names}.")

        if request_fields is None:
            request_fields = self._get_request_fields()

        if response_fields is None:
            response_fields = self._get_response_fields()

        user_fields = set(request_fields + response_fields)
        self.validate_field_names(user_fields)

        if owner_field in request_fields:
            request_fields.remove(owner_field)

        if owner_field in response_fields:
            response_fields.remove(owner_field)

        self.instance_schema = schema_for_instance(model, response_fields)

        fields_for_new = request_fields
        self.new_instance_schema = schema_for_new_instance(model, self.instance_schema, fields_for_new)
        self.multiple_instance_schema = schema_for_multiple_models(model, self.instance_schema)

        if authentication is None:
            self.authentication = lambda: None
        else:
            self.authentication = authentication

        self.get_function = self.get_identifier_function()

    def _get_request_fields(self):
        model_fields = self.model._meta.get_fields()
        fields = []
        for field in model_fields:
            if field.name == self.model_identifier:
                continue
            if field.concrete and (
                not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)
            ):
                if field.editable and not field.auto_created:
                    fields.append(field.name)
            else:
                if field.editable and not field.auto_created:
                    fields.append(field.name)
        return fields

    def _get_response_fields(self):
        response_fields = []
        model_fields = self.model._meta.get_fields()
        for field in model_fields:
            if field.name == "id":
                if self.model_identifier != "id":
                    continue
            response_fields.append(field.name)
        return response_fields

    def validate_field_names(self, user_fields):
        model_fields = self.model._meta.get_fields()
        valid_fields_names = sorted({field.name for field in model_fields})
        invalid_fields = sorted(user_fields.difference(valid_fields_names))
        if invalid_fields:
            raise InvalidFieldsException(f"{invalid_fields} not in {valid_fields_names}")

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

    def check_query_filter(self, instance, user):
        if not self.model.objects.filter(self.query_filter(user)).filter(pk=instance.pk).exists():
            logger.warning("User %s tried to get %s and it is not allowed.", user, instance)
            raise HTTPException(status_code=404, detail="Object not found.")

    def check_ownership(self, instance, user):
        if not user == getattr(instance, self.owner_field):
            owner = getattr(instance, self.owner_field)
            logger.warning("User %s tried to update %s and is not the owner, owner is %s.", user, instance, owner)
            raise HTTPException(status_code=404, detail="Object not found.")

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

    def add_all_routes(self, router):
        self.add_list_route_to_router(router)
        self.add_get_route_to_router(router)
        self.add_create_route_to_router(router)
        self.add_update_route_to_router(router)
        self.add_delete_route_to_router(router)

    def add_list_route_to_router(self, router):
        @router.get(
            self.path_for_list_and_post,
            summary=f"Retrieve a list of all the {self.name_plural}.",
            tags=[f"{self.name_plural}"],
            response_model=self.multiple_instance_schema,
            name=f"{self.name_lower_plural}-get",
        )
        def _get(user: User = Depends(self.authentication)) -> self.multiple_instance_schema:
            filter_models = self.model.objects.all()

            if self.query_filter:
                filter_models = filter_models.filter(self.query_filter(user))

            if self.owner_field:
                filter_models = filter_models.filter(**{self.owner_field: user})

            return self.multiple_instance_schema.from_qs(filter_models)

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
            user: User = Depends(self.authentication),
        ) -> self.instance_schema:

            if self.query_filter:
                self.check_query_filter(instance, user)

            if self.owner_field:
                self.check_ownership(instance, user)

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
            api_instance: self.new_instance_schema, user: User = Depends(self.authentication)
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
            user: User = Depends(self.authentication),
        ) -> self.instance_schema:

            if self.query_filter:
                self.check_query_filter(instance, user)

            if self.owner_field:
                self.check_ownership(instance, user)

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
            instance: self.model = Depends(self.get_function), user: User = Depends(self.authentication)
        ) -> self.instance_schema:

            if self.query_filter:
                self.check_query_filter(instance, user)

            if self.owner_field:
                self.check_ownership(instance, user)

            api_instance = self.instance_schema.from_model(instance)
            instance.delete()
            return api_instance

        return _delete
