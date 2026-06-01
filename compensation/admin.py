from django.contrib import admin

from .models import Compensation


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "normalized_job_title",
        "experience_level",
        "total_compensation",
        "is_verified",
        "is_flagged",
    )

    search_fields = (
        "company__name",
        "job_title",
    )

    list_filter = (
        "experience_level",
        "is_verified",
        "is_flagged",
    )

    readonly_fields = (
        "normalized_job_title",
        "total_compensation",
    )