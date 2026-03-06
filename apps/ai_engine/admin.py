from django.contrib import admin
from .models import AIProviderSetting, AIGeneratedMessage


@admin.register(AIProviderSetting)
class AIProviderSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "provider",
        "model_name",
        "is_active",
        "created_at",
    )
    search_fields = ("workspace__company_name", "provider", "model_name")
    list_filter = ("provider", "is_active", "created_at")


@admin.register(AIGeneratedMessage)
class AIGeneratedMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "campaign",
        "lead",
        "message_type",
        "generated_subject",
        "created_by",
        "created_at",
    )
    search_fields = (
        "workspace__company_name",
        "lead__email",
        "campaign__name",
        "generated_subject",
    )
    list_filter = ("message_type", "created_at")