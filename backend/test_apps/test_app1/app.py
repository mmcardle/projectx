from uuid import UUID

from django.apps import AppConfig
from django.contrib.auth import get_user_model

from api.routing import router
from users.app import get_current_user_func, schema_for_django_user


class TestApp1Config(AppConfig):
    name = "test_app1"
    verbose_name = "The test App 1"

    def ready(self):
        from api.fastapi import RouteBuilder  # pylint: disable=import-outside-toplevel

        self.add_test_model_routes(RouteBuilder)
        self.add_test_model_with_owner_routes(RouteBuilder)
        self.add_test_model_with_jwt_user(RouteBuilder)
        self.add_test_related_model(RouteBuilder)

        for route in router.routes:
            print(f"Added test route: {route.path}")

    def add_test_model_routes(self, route_builder_class):

        TestModel = self.get_model("TestModel")  # pylint: disable=invalid-name

        request_fields = ["name", "config"]
        read_only_fields = ["last_updated", "created"]
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        simple_route_builder = route_builder_class(TestModel, request_fields, response_fields, read_only_fields, config)

        simple_route_builder.add_list_route_to_router(router)
        simple_route_builder.add_get_route_to_router(router)
        simple_route_builder.add_create_route_to_router(router)
        simple_route_builder.add_update_route_to_router(router)
        simple_route_builder.add_delete_route_to_router(router)

    def add_test_related_model(self, route_builder_class):

        TestModelWithRelationship = self.get_model("TestModelWithRelationship")  # pylint: disable=invalid-name

        request_fields = ["name", "related_model"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields + read_only_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        simple_route_builder = route_builder_class(
            TestModelWithRelationship, request_fields, response_fields, read_only_fields, config
        )

        simple_route_builder.add_list_route_to_router(router)
        simple_route_builder.add_get_route_to_router(router)
        simple_route_builder.add_create_route_to_router(router)
        simple_route_builder.add_update_route_to_router(router)
        simple_route_builder.add_delete_route_to_router(router)

    def add_test_model_with_owner_routes(self, route_builder_class):

        TestModelWithOwner = self.get_model("TestModelWithOwner")  # pylint: disable=invalid-name

        request_fields = ["name"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields
        config = {"identifier": "uuid", "identifier_class": UUID}

        route_builder = route_builder_class(
            TestModelWithOwner, request_fields, response_fields, read_only_fields, config, owner_field="owner"
        )
        route_builder.add_list_route_to_router(router)
        route_builder.add_get_route_to_router(router)
        route_builder.add_create_route_to_router(router)
        route_builder.add_update_route_to_router(router)
        route_builder.add_delete_route_to_router(router)

    def add_test_model_with_jwt_user(self, route_builder_class):

        TestModel = self.get_model("TestModel")  # pylint: disable=invalid-name

        request_fields = ["name"]
        read_only_fields = []
        response_fields = ["uuid"] + request_fields
        config = {
            "identifier": "uuid",
            "identifier_class": UUID,
            "name": "testmodelwithJWT",
        }

        User = get_user_model()  # pylint: disable=invalid-name

        DjangoUserSchema = schema_for_django_user(["public_uuid", "email", "first_name", "last_name", "is_active"])

        def get_user(username: str):
            try:
                user = User.objects.get(username=username)
                return DjangoUserSchema.from_model(user)
            except User.DoesNotExist:
                return None

        current_user_function = get_current_user_func(get_user)

        route_builder = route_builder_class(
            TestModel,
            request_fields,
            response_fields,
            read_only_fields,
            config,
            current_user_function=current_user_function,
        )
        route_builder.add_list_route_to_router(router)
        route_builder.add_get_route_to_router(router)
        route_builder.add_create_route_to_router(router)
        route_builder.add_update_route_to_router(router)
        route_builder.add_delete_route_to_router(router)
