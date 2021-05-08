from uuid import UUID

from django.apps import AppConfig

from api.routing import router


class TestAppWithRelatedModelConfig(AppConfig):
    name = "test_app_with_related_model"

    def ready(self):

        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel

        TestModelWithRelationship = self.get_model("TestModelWithRelationship")  # pylint: disable=invalid-name

        request_fields = ["name", "related_model"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = RouteBuilder(
            TestModelWithRelationship,
            request_fields,
            response_fields,
            read_only_fields,
            config,
        )

        route_builder.add_all_routes(router)
