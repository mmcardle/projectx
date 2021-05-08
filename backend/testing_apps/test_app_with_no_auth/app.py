from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class TestAppWithNoAuthenticationConfig(AppConfig):
    name = "test_app_with_no_auth"

    def ready(self):

        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel

        TestModel = self.get_model("UnauthenticatedTestModel")  # pylint: disable=invalid-name

        request_fields = ["name"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(
            TestModel, request_fields, response_fields, read_only_fields, config, authentication=None
        )

        route_builder.add_all_routes(router)
