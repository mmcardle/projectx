from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class TestAppWithAPIKeyConfig(AppConfig):
    name = "test_app_with_api_key"

    def ready(self):

        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel
        from api.fastapi import check_api_key  # pylint: disable=import-outside-toplevel

        TestModel = self.get_model("TestModel")  # pylint: disable=invalid-name

        request_fields = ["name", "config"]
        read_only_fields = ["last_updated", "created"]
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(
            TestModel, request_fields, response_fields, read_only_fields, config, authentication=check_api_key
        )

        route_builder.add_all_routes(router)
