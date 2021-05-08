from uuid import UUID

from django.apps import AppConfig

from api.routing import router
from users.app import get_user_authentication


class TestAppWithJWTUserConfig(AppConfig):
    name = "test_app_with_jwt_user"

    def ready(self):
        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel

        TestModelWithJWT = self.get_model("TestModelWithJWT")  # pylint: disable=invalid-name

        request_fields = ["name"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields
        config = {
            "identifier": "uuid",
            "identifier_class": UUID,
        }

        authentication, _ = get_user_authentication()

        route_builder = RouteBuilder(
            TestModelWithJWT,
            request_fields,
            response_fields,
            read_only_fields,
            config,
            authentication=authentication,
        )
        route_builder.add_all_routes(router)
