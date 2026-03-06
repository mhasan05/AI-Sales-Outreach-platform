from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "email", "full_name", "role", "is_staff", "is_active")
    search_fields = ("username", "email", "full_name")
    ordering = ("id",)

    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("full_name", "role", "is_email_verified")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Info", {"fields": ("email", "full_name", "role")}),
    )