import logging

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from . import models


logger = logging.getLogger(__name__)


def send_activation_email(_, request, queryset):
    for user in queryset:
        user.send_activation_email(request)
        message = "%s Activation Email Sent." % user
        messages.info(request, message)
        logger.info(message)


class UserAdmin(UserAdmin):

    actions = [send_activation_email]

    readonly_fields = ("public_uuid", "modified", "created")
    list_display = ("public_uuid", "email", "is_active", "is_staff", "created", "modified")
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
