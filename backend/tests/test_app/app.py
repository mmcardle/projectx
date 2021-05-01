from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class TestAppConfig(AppConfig):
    name = "test_app"

    def ready(self):
        from api.fastapi import RouteBuilder

        TestModel = self.get_model("TestModel")  # pylint: disable=invalid-name

        request_fields = ["name", "config"]
        read_only_fields = ["last_updated", "created"]
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(TestModel, request_fields, response_fields, read_only_fields, config)

        route_builder.add_list_route_to_router(router)
        route_builder.add_get_route_to_router(router)
        route_builder.add_create_route_to_router(router)
        route_builder.add_update_route_to_router(router)
        route_builder.add_delete_route_to_router(router)
