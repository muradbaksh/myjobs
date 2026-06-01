from django.contrib import admin

from .models import CompanyReview


@admin.register(CompanyReview)
class CompanyReviewAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "user",
        "weighted_score",
        "is_verified",
        "is_flagged",
        "created_at",
    )

    list_filter = (
        "is_verified",
        "is_flagged",
        "overall_recommendation",
    )

    search_fields = (
        "company__name",
        "user__email",
    )

    readonly_fields = (
        "anonymous_reference",
        "weighted_score",
    )