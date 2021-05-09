from uuid import UUID

from django.apps import AppConfig

from api.routing import router
from users.app import get_user_authentication


class TestAppWithJWTUserConfig(AppConfig):
    name = "test_app_with_jwt_user"

    def ready(self):
        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel

        TestModelWithJWT = self.get_model("TestModelWithJWT")  # pylint: disable=invalid-name

        authentication, _ = get_user_authentication()

        route_builder = RouteBuilder(
            TestModelWithJWT,
            request_fields=["name"],
            response_fields=["name", "uuid"],
            config={"identifier": "uuid", "identifier_class": UUID},
            authentication=authentication,
        )
        route_builder.add_all_routes(router)
