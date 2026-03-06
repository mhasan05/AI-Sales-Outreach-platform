from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("owner", "Owner"),
        ("staff", "Staff"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="owner")
    is_email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email", "full_name"]

    def __str__(self):
        return self.email