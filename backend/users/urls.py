from django.urls import path, include

from . import views

urlpatterns = (
    path("users/User/", views.UserListView.as_view(), name="users_User_list"),
    path("users/User/create/", views.UserCreateView.as_view(), name="users_User_create"),
    path("users/User/detail/<int:pk>/", views.UserDetailView.as_view(), name="users_User_detail"),
    path("users/User/update/<int:pk>/", views.UserUpdateView.as_view(), name="users_User_update"),
)
