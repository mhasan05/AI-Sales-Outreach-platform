from django.db import models
from apps.workspace.models import Workspace
from apps.leads.models import Lead
from apps.campaigns.models import Campaign, CampaignSequenceStep


class AIProviderSetting(models.Model):
    PROVIDER_CHOICES = (
        ("openai", "OpenAI"),
    )

    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.CASCADE,
        related_name="ai_provider_setting"
    )
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default="openai")
    api_key = models.CharField(max_length=500)
    model_name = models.CharField(max_length=150, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_provider_settings"

    def __str__(self):
        return f"{self.workspace.company_name} - {self.provider}"


class AIGeneratedMessage(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ("initial", "Initial"),
        ("follow_up", "Follow Up"),
        ("custom", "Custom"),
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="ai_generated_messages"
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="ai_generated_messages",
        blank=True,
        null=True
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="ai_generated_messages",
        blank=True,
        null=True
    )
    sequence_step = models.ForeignKey(
        CampaignSequenceStep,
        on_delete=models.SET_NULL,
        related_name="generated_messages",
        blank=True,
        null=True
    )

    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES, default="initial")

    input_prompt = models.TextField(blank=True, null=True)
    generated_subject = models.CharField(max_length=255, blank=True, null=True)
    generated_body = models.TextField()

    variables_snapshot = models.JSONField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="ai_generated_messages"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_generated_messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.message_type} - {self.created_at}"