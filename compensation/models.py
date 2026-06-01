from django.db import models
from django.conf import settings
from companies.models import Company

class Compensation(models.Model):

    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("intern", "Internship"),
    ]

    EXPERIENCE_LEVELS = [
        ("junior", "Junior"),
        ("mid", "Mid Level"),
        ("senior", "Senior"),
        ("lead", "Lead"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="compensations"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="compensations"
    )

    # =========================
    # Job Information
    # =========================

    job_title = models.CharField(
        max_length=255
    )

    normalized_job_title = models.CharField(
        max_length=255,
        blank=True
    )

    department = models.CharField(
        max_length=255
    )

    employment_type = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_TYPES
    )

    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_LEVELS
    )

    years_of_experience = models.PositiveIntegerField(
        default=0
    )

    location = models.CharField(
        max_length=255
    )

    # =========================
    # Compensation Information
    # =========================

    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    allowances = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    other_benefits = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    market_fairness_rating = models.PositiveSmallIntegerField()

    # =========================
    # Anonymous System
    # =========================

    anonymous = models.BooleanField(
        default=True
    )

    anonymous_reference = models.UUIDField(
        editable=False,
        null=True,
        blank=True
    )

    # =========================
    # Security & Moderation
    # =========================

    is_verified = models.BooleanField(
        default=False
    )

    is_flagged = models.BooleanField(
        default=False
    )

    moderation_note = models.TextField(
        blank=True,
        null=True
    )

    # =========================
    # Analytics
    # =========================

    total_compensation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["normalized_job_title"]),
            models.Index(fields=["experience_level"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):

        return f"{self.company.name} - {self.job_title}"