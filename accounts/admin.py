from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin, ModelAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "company_name",
        "phone",
        "is_staff",
    )
    list_filter = UserAdmin.list_filter + ("role",)
    search_fields = UserAdmin.search_fields + ("company_name", "phone")

    fieldsets = UserAdmin.fieldsets + (
        (_("Catalog profile"), {"fields": ("role", "company_name", "phone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Catalog profile"), {"fields": ("role", "company_name", "phone")}),
    )
