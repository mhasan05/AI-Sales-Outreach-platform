from django.db import models
from apps.workspace.models import Workspace
from apps.leads.models import Lead
from apps.campaigns.models import Campaign, CampaignLead, CampaignSequenceStep


class SMTPSetting(models.Model):
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.CASCADE,
        related_name="smtp_setting"
    )
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=500)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField()
    from_name = models.CharField(max_length=255, blank=True, null=True)
    reply_to_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "smtp_settings"

    def __str__(self):
        return f"{self.workspace.company_name} SMTP"


class EmailLog(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="email_logs"
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="email_logs"
    )
    campaign_lead = models.ForeignKey(
        CampaignLead,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="email_logs"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="email_logs"
    )
    sequence_step = models.ForeignKey(
        CampaignSequenceStep,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="email_logs"
    )

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()

    provider_message_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True, null=True)

    sent_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_email_logs"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.to_email} - {self.subject}"