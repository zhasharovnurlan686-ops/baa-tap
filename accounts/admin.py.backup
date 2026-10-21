from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("BaaTap KG", {"fields": ("role", "company_name", "city", "phone", "about")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("BaaTap KG", {"fields": ("role", "company_name", "city", "phone", "about")}),)
    list_display = ("username", "email", "company_name", "role", "city", "is_staff")
    list_filter = ("role", "city", "is_staff")
