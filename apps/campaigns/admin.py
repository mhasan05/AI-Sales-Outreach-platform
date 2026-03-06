from django.contrib import admin
from .models import Campaign, CampaignLead, CampaignSequenceStep


class CampaignLeadInline(admin.TabularInline):
    model = CampaignLead
    extra = 0


class CampaignSequenceStepInline(admin.TabularInline):
    model = CampaignSequenceStep
    extra = 0


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "workspace",
        "status",
        "daily_send_limit",
        "start_date",
        "end_date",
        "created_at",
    )
    search_fields = ("name", "workspace__company_name", "objective")
    list_filter = ("status", "created_at", "start_date", "end_date")
    inlines = [CampaignLeadInline, CampaignSequenceStepInline]


@admin.register(CampaignLead)
class CampaignLeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "campaign",
        "lead",
        "status",
        "last_contacted_at",
        "next_follow_up_at",
        "created_at",
    )
    search_fields = ("campaign__name", "lead__email", "lead__first_name", "lead__company_name")
    list_filter = ("status", "created_at")


@admin.register(CampaignSequenceStep)
class CampaignSequenceStepAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "campaign",
        "step_number",
        "step_type",
        "delay_days",
        "is_ai_generated",
        "is_active",
    )
    search_fields = ("campaign__name", "subject")
    list_filter = ("step_type", "is_ai_generated", "is_active")