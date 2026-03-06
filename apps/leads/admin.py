from django.contrib import admin
from .models import Lead, LeadTag


@admin.register(LeadTag)
class LeadTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace")
    search_fields = ("name", "workspace__company_name")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "company_name",
        "status",
        "workspace",
        "created_at",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "company_name",
        "job_title",
    )
    list_filter = ("status", "created_at", "workspace")