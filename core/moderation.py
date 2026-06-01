from django.db import models

from django.conf import settings


class ContentReport(models.Model):

    REPORT_TYPES = [
        ("spam", "Spam"),
        ("fake", "Fake"),
        ("abuse", "Abusive"),
        ("misleading", "Misleading"),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content_type = models.CharField(
        max_length=255
    )

    object_id = models.CharField(
        max_length=255
    )

    reason = models.CharField(
        max_length=50,
        choices=REPORT_TYPES
    )

    description = models.TextField(
        blank=True
    )

    resolved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.content_type} - {self.reason}"