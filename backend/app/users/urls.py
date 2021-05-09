from django.urls import path

from users import api

urlpatterns = (
    path("user/", api.user_details, name="user_api_user"),
    path("register/", api.register, name="user_api_register"),
    path("activate/", api.activate, name="user_api_activate"),
    path("login/", api.login, name="user_api_login"),
    path("logout/", api.logout, name="user_api_logout"),
    path("change_details/", api.change_details, name="user_api_change_details"),
    path("change_password/", api.change_password, name="user_api_change_password"),
    path("reset_password/", api.reset_password, name="user_api_reset_password"),
    path("reset_password_check/", api.reset_password_check, name="user_api_reset_password_check"),
    path("reset_password_complete/", api.reset_password_complete, name="user_api_reset_password_complete"),
)
