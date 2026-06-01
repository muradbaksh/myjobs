from django.db import models

from django.conf import settings


class AuditLog(models.Model):

    ACTION_TYPES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("moderate", "Moderate"),
        ("login", "Login"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_TYPES
    )

    object_type = models.CharField(
        max_length=255
    )

    object_id = models.CharField(
        max_length=255
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    metadata = models.JSONField(
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.user} - {self.action}"