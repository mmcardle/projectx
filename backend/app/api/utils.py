from uuid import UUID
from pydantic import BaseModel
from django.db import models
from fastapi import APIRouter, Header, HTTPException, Path, Depends, Body

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



def get_config_for_model(model, defaults):
    # TODO - slugify name for urls
    name = defaults.get("name", model.__name__)
    name_plural = f"{name}s"
    name_lower = defaults.get("name", model.__name__).lower()
    name_lower_plural = f"{name_lower}s"
    return name, name_plural, name_lower, name_lower_plural


def add_list_route(router: APIRouter, model: models.Model, response_model: BaseModel, config: dict = {}):

    name, name_plural, name_lower, name_lower_plural = get_config_for_model(model, config)

    @router.get(
        f"/{name_lower_plural}/",
        summary=f"Retrieve a list of all the {name_plural}.",
        tags=[f"{name_plural}"],
        response_model=response_model,
        name=f"{name_lower_plural}-get",
    )
    def _get(_: model = Depends(check_api_key)) -> response_model:
        all_models = model.objects.all()
        return response_model.from_qs(all_models)


def add_get_route(router: APIRouter, model: models.Model, response_model: BaseModel, get_function, config: dict = {}):

    name, name_plural, name_lower, name_lower_plural = get_config_for_model(model, config)

    @router.get(
        f"/{name_lower_plural}/{{uuid}}/",
        summary=f"Get a {name}.",
        tags=[f"{name_plural}"],
        response_model=response_model,
        name=f"{name_lower}-get",
    )
    def _get(
        instance: response_model = Depends(get_function),
        _: User = Depends(check_api_key),
    ) -> response_model:
        return response_model.from_model(instance)


def add_create_route(router: APIRouter, model: models.Model, request_model: BaseModel, response_model: BaseModel, config: dict = {}):

    name, name_plural, name_lower, name_lower_plural = get_config_for_model(model, config)

    @router.post(
        f"/{name_lower_plural}/{{uuid}}/",
        summary=f"Create a new {name}.",
        tags=[f"{name_plural}"],
        response_model=response_model,
        name=f"{name_lower_plural}-post",
    )
    def _post(api_instance: request_model, _: User = Depends(check_api_key)) -> response_model:
        instance = api_instance.new_project()
        return response_model.from_model(instance)


def add_update_route(router: APIRouter, model: models.Model, response_model: BaseModel, get_function, config: dict = {}):

    name, name_plural, name_lower, name_lower_plural = get_config_for_model(model, config)

    @router.put(
        f"/{name_lower_plural}/{{uuid}}/",
        summary=f"Update a {name}.",
        tags=[f"{name_plural}"],
        response_model=response_model,
        name=f"{name_lower}-put",
    )
    def _put(
        instance: model = Depends(get_function),
        api_instance: response_model = Body(...),
        _: User = Depends(check_api_key),
    ) -> response_model:
        return response_model.update_project(instance)


def add_delete_route(router: APIRouter, model: models.Model, response_model: BaseModel, get_function, config: dict = {}):

    name, name_plural, name_lower, name_lower_plural = get_config_for_model(model, config)

    @router.delete(
        f"/{name_lower_plural}/{{uuid}}/",
        summary=f"Delete a {name}.",
        tags=[f"{name_plural}"],
        response_model=response_model,
        name=f"{name_lower}-delete",
    )
    def _delete(instance: model = Depends(get_function), _: User = Depends(check_api_key)) -> response_model:
        api_instance = response_model.from_model(instance)
        instance.delete()
        return api_project
