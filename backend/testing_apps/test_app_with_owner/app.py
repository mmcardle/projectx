from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class TestAppWithOwnerConfig(AppConfig):
    name = "test_app_with_owner"

    def ready(self):
        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel
        from api.fastapi import check_api_key  # pylint: disable=import-outside-toplevel

        TestModelWithOwner = self.get_model("TestModelWithOwner")  # pylint: disable=invalid-name

        request_fields = ["name"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(
            TestModelWithOwner,
            request_fields,
            response_fields,
            read_only_fields,
            config,
            owner_field="owner",
            authentication=check_api_key,
        )
        route_builder.add_all_routes(router)
