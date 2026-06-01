from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "industry",
        "company_type",
        "verified",
        "review_count",
        "reputation_index",
    )

    search_fields = (
        "name",
        "industry",
    )

    list_filter = (
        "industry",
        "verified",
        "company_type",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    readonly_fields = (
        "review_count",
        "reputation_index",
    )