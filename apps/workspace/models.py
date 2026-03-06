from django.conf import settings
from django.db import models


class Workspace(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace"
    )
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True, null=True)
    business_type = models.CharField(max_length=150, blank=True, null=True)
    industry = models.CharField(max_length=150, blank=True, null=True)
    company_size = models.CharField(max_length=100, blank=True, null=True)

    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    sender_position = models.CharField(max_length=150, blank=True, null=True)

    business_description = models.TextField(blank=True, null=True)
    product_service_summary = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    unique_selling_points = models.TextField(blank=True, null=True)

    default_email_tone = models.CharField(
        max_length=50,
        choices=(
            ("professional", "Professional"),
            ("friendly", "Friendly"),
            ("formal", "Formal"),
            ("direct", "Direct"),
        ),
        default="professional"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workspaces"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company_name} - {self.owner.email}"