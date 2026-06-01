from django.db import transaction
from uuid import uuid4

from compensation.analytics import (
    CompensationAnalytics
)

from accounts.services import CreditService


class CompensationService:

    COMPENSATION_VIEW_COST = 5

    @staticmethod
    def generate_anonymous_reference():
        """Generate anonymous UUID reference for compensation data."""
        return uuid4()

    @staticmethod
    def normalize_job_title(title):

        title = title.lower().strip()

        mappings = {
            "software engineer":
                "Software Engineer",

            "swe":
                "Software Engineer",

            "backend developer":
                "Backend Developer",

            "frontend developer":
                "Frontend Developer",
        }

        return mappings.get(
            title,
            title.title()
        )

    @staticmethod
    def calculate_total_compensation(data):

        return (
            data["base_salary"]
            + data["allowances"]
            + data["bonus"]
            + data["other_benefits"]
        )

    @staticmethod
    @transaction.atomic
    def process_compensation_creation(compensation):

        compensation.normalized_job_title = (
            CompensationService.normalize_job_title(
                compensation.job_title
            )
        )

        compensation.total_compensation = (
            CompensationService.calculate_total_compensation({
                "base_salary":
                    compensation.base_salary,

                "allowances":
                    compensation.allowances,

                "bonus":
                    compensation.bonus,

                "other_benefits":
                    compensation.other_benefits,
            })
        )

        # Generate anonymous reference
        compensation.anonymous_reference = (
            CompensationService.generate_anonymous_reference()
        )

        compensation.save()
        
        # Award credits for compensation submission
        CreditService.add_credits(
            compensation.user,
            5,  # Compensation submission bonus
            transaction_type="compensation_submission",
            description=f"Compensation data submitted for {compensation.company.name} - {compensation.job_title}",
            related_object_id=str(compensation.id)
        )

    @staticmethod
    def deduct_benchmark_credits(user):
        """Deduct credits when user accesses salary benchmark data."""
        CreditService.deduct_credits(
            user,
            CompensationService.COMPENSATION_VIEW_COST,
            transaction_type="benchmark_access",
            description="Salary benchmark access"
        )