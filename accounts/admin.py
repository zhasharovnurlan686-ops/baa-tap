from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("BaaTap KG — компания", {
            "fields": (
                "role",
                "company_name",
                "company_registration_number",
                "verification_status",
                "city",
                "phone",
                "about",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("BaaTap KG — компания", {
            "fields": (
                "role",
                "company_name",
                "company_registration_number",
                "verification_status",
                "city",
                "phone",
                "about",
            )
        }),
    )

    list_display = (
        "username",
        "email",
        "company_name",
        "role",
        "verification_status",
        "city",
        "is_staff",
    )

    list_filter = (
        "role",
        "verification_status",
        "city",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "company_name",
        "company_registration_number",
    )

    ordering = ("username",)
