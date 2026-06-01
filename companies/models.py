from django.db import models

from django.utils.text import slugify


class Company(models.Model):

    COMPANY_TYPES = [
        ("local", "Local"),
        ("mnc", "Multinational"),
        ("startup", "Startup"),
    ]

    INDUSTRY_CHOICES = [
        ("software", "Software"),
        ("banking", "Banking"),
        ("telecom", "Telecom"),
        ("healthcare", "Healthcare"),
        ("ecommerce", "E-Commerce"),
    ]

    SIZE_CHOICES = [
        ("1-50", "1-50"),
        ("51-200", "51-200"),
        ("201-500", "201-500"),
        ("500+", "500+"),
    ]

    name = models.CharField(
        max_length=255,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    company_type = models.CharField(
        max_length=20,
        choices=COMPANY_TYPES
    )

    industry = models.CharField(
        max_length=100,
        choices=INDUSTRY_CHOICES
    )

    manpower_size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES
    )

    headquarters = models.CharField(
        max_length=255
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    logo = models.ImageField(
        upload_to="companies/logos/",
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    verified = models.BooleanField(
        default=False
    )

    review_count = models.PositiveIntegerField(
        default=0
    )

    compensation_count = models.PositiveIntegerField(
        default=0
    )

    reputation_index = models.FloatField(
        default=0
    )

    average_salary_score = models.FloatField(
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
            models.Index(fields=["name"]),
            models.Index(fields=["industry"]),
            models.Index(fields=["verified"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name