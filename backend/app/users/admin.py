from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


class UserAdmin(UserAdmin):
    readonly_fields = ("public_uuid", "modified", "created")
    list_display = ("public_uuid", "email", "created", "modified")
    list_filter = ("is_active", "is_staff", "groups")
    search_fields = ("email", "public_uuid")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)

admin.site.register(models.User, UserAdmin)
