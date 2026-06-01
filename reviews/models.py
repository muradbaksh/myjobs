from django.db import models
from django.conf import settings
from companies.models import Company


class CompanyReview(models.Model):

    RECOMMENDATION_CHOICES = [
        ("yes", "Yes"),
        ("neutral", "Neutral"),
        ("no", "No"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    # =========================
    # 10 Structured Questions
    # =========================

    company_brand_value = models.PositiveSmallIntegerField()
    work_environment = models.PositiveSmallIntegerField()
    career_growth = models.PositiveSmallIntegerField()
    salary_satisfaction = models.PositiveSmallIntegerField()
    fringe_benefits = models.PositiveSmallIntegerField()
    job_security = models.PositiveSmallIntegerField()
    employee_respect = models.PositiveSmallIntegerField()
    management_quality = models.PositiveSmallIntegerField()
    work_life_balance = models.PositiveSmallIntegerField()
    learning_opportunity = models.PositiveSmallIntegerField()
    overall_recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES
    )
    review_text = models.TextField(
        blank=True,
        null=True
    )

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
    # Moderation System
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

    weighted_score = models.FloatField(
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

        unique_together = [
            "user",
            "company"
        ]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["is_flagged"]),
        ]

    def __str__(self):

        return f"{self.company.name} Review"