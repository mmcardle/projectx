# pylint: disable=import-outside-toplevel
from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):

        from api.fastapi import RouteBuilder

        User = self.get_model("User")  # pylint: disable=invalid-name

        request_fields = ["email", "first_name", "last_name"]
        response_fields = ["public_uuid", "email", "first_name", "last_name"]
        config = {"identifier": "public_uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(User, request_fields, response_fields, config)

        # route_builder.add_list_route_to_router(router)
        route_builder.add_get_route_to_router(router)
        route_builder.add_create_route_to_router(router)
        route_builder.add_update_route_to_router(router)
        route_builder.add_delete_route_to_router(router)
