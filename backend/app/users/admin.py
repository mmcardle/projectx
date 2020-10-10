from django.contrib import admin
from django import forms

from . import models


class UserAdminForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = "__all__"


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = [
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "last_updated",
        "created",
    ]


admin.site.register(models.User, UserAdmin)
