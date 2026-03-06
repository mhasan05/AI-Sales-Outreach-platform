from django.db import models
from apps.workspace.models import Workspace
from apps.leads.models import Lead


class Campaign(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    objective = models.CharField(max_length=255, blank=True, null=True)

    target_audience = models.TextField(blank=True, null=True)
    offer_summary = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="draft")

    daily_send_limit = models.PositiveIntegerField(default=50)
    follow_up_gap_days = models.PositiveIntegerField(default=3)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaigns"
        ordering = ["-created_at"]
        unique_together = ("workspace", "name")

    def __str__(self):
        return self.name


class CampaignLead(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("queued", "Queued"),
        ("contacted", "Contacted"),
        ("replied", "Replied"),
        ("interested", "Interested"),
        ("not_interested", "Not Interested"),
        ("meeting_booked", "Meeting Booked"),
        ("completed", "Completed"),
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="campaign_leads"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="lead_campaigns"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    last_contacted_at = models.DateTimeField(blank=True, null=True)
    next_follow_up_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "campaign_leads"
        unique_together = ("campaign", "lead")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campaign.name} - {self.lead.email}"


class CampaignSequenceStep(models.Model):
    STEP_TYPE_CHOICES = (
        ("initial", "Initial Email"),
        ("follow_up", "Follow Up"),
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="sequence_steps"
    )
    step_number = models.PositiveIntegerField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default="follow_up")
    delay_days = models.PositiveIntegerField(default=0)

    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    is_ai_generated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaign_sequence_steps"
        ordering = ["step_number"]
        unique_together = ("campaign", "step_number")

    def __str__(self):
        return f"{self.campaign.name} - Step {self.step_number}"