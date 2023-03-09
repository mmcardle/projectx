import logging

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from projectx.users import models

logger = logging.getLogger(__name__)


def send_activation_email(_, request, queryset):
    for user in queryset:
        user.send_account_activation_email(request)
        message = f"{user} Activation Email Sent."
        messages.info(request, message)
        logger.info(message)


class ProjectXUserAdmin(UserAdmin):
    actions = [send_activation_email]

    readonly_fields = ("public_uuid", "modified", "created")
    list_display = ("public_uuid", "email", "display_name", "is_active", "is_staff", "created", "modified")
    list_filter = ("is_active", "is_staff", "groups")
    search_fields = ("email", "public_uuid")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Details", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


admin.site.register(models.User, ProjectXUserAdmin)
