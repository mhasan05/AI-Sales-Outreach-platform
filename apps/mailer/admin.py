from django.contrib import admin
from .models import SMTPSetting, EmailLog


@admin.register(SMTPSetting)
class SMTPSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "host",
        "port",
        "username",
        "from_email",
        "is_active",
        "created_at",
    )
    search_fields = ("workspace__company_name", "host", "username", "from_email")
    list_filter = ("use_tls", "use_ssl", "is_active", "created_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "to_email",
        "campaign",
        "lead",
        "status",
        "sent_at",
        "created_at",
    )
    search_fields = ("to_email", "subject", "lead__email", "campaign__name")
    list_filter = ("status", "sent_at", "created_at")