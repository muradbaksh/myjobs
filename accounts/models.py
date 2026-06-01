import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("user", "User"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
        ("analyst", "Analyst"),
    ]
    INDUSTRY_CHOICES = [
        ("software", "Software"),
        ("banking", "Banking"),
        ("telecom", "Telecom"),
        ("healthcare", "Healthcare"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        unique=True
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    full_name = models.CharField(
        max_length=255
    )

    industry = models.CharField(
        max_length=100,
        choices=INDUSTRY_CHOICES,
        blank=True,
        null=True
    )

    years_of_experience = models.PositiveIntegerField(
        default=0
    )

    professional_email = models.EmailField(
        blank=True,
        null=True
    )

    linkedin_url = models.URLField(
        blank=True,
        null=True
    )

    credits = models.PositiveIntegerField(
        default=0
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user"
    )
    anonymous_identity = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    is_verified_professional = models.BooleanField(
        default=False
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    is_staff = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class CreditTransaction(models.Model):
    """
    Audit trail for all credit operations.
    Tracks when users earn or spend credits and the reason.
    """
    
    TRANSACTION_TYPES = [
        ("review_submission", "Review Submission"),
        ("compensation_submission", "Compensation Submission"),
        ("benchmark_access", "Benchmark Access"),
        ("admin_adjustment", "Admin Adjustment"),
        ("referral_bonus", "Referral Bonus"),
    ]
    
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("failed", "Failed"),
        ("reversed", "Reversed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="credit_transactions"
    )

    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES
    )

    amount = models.IntegerField()  # Can be positive or negative

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed"
    )

    balance_before = models.PositiveIntegerField()

    balance_after = models.PositiveIntegerField()

    description = models.TextField(
        blank=True,
        null=True
    )

    related_object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reference to related review/compensation ID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: {self.amount}"