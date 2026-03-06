from django.db import models
from apps.workspace.models import Workspace


class LeadTag(models.Model):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="lead_tags"
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "lead_tags"
        unique_together = ("workspace", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lead(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("contacted", "Contacted"),
        ("replied", "Replied"),
        ("interested", "Interested"),
        ("not_interested", "Not Interested"),
        ("meeting_booked", "Meeting Booked"),
        ("closed", "Closed"),
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="leads"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)

    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=150, blank=True, null=True)
    job_title = models.CharField(max_length=150, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(LeadTag, blank=True, related_name="leads")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leads"
        ordering = ["-created_at"]
        unique_together = ("workspace", "email")

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} - {self.email}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()