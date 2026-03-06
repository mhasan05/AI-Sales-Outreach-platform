from django.contrib import admin
from .models import Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_name",
        "owner",
        "sender_email",
        "default_email_tone",
        "is_active",
        "created_at",
    )
    search_fields = ("company_name", "owner__email", "sender_email", "sender_name")
    list_filter = ("default_email_tone", "is_active", "created_at")