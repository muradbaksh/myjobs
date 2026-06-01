from django.db.models import Avg

from reviews.models import CompanyReview

from .models import Company


class CompanyService:

    @staticmethod
    def update_reputation_index(company_id):
        """
        Calculate company reputation index using weighted average of all 10 review fields.
        This ensures a comprehensive reputation score based on all evaluation criteria.
        """
        company = Company.objects.get(id=company_id)

        reviews = CompanyReview.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        )

        if not reviews.exists():
            company.review_count = 0
            company.reputation_index = 0
            company.save()
            return

        reputation_score = reviews.aggregate(
            avg_brand_value=Avg("company_brand_value"),
            avg_environment=Avg("work_environment"),
            avg_growth=Avg("career_growth"),
            avg_salary=Avg("salary_satisfaction"),
            avg_benefits=Avg("fringe_benefits"),
            avg_security=Avg("job_security"),
            avg_respect=Avg("employee_respect"),
            avg_management=Avg("management_quality"),
            avg_work_life=Avg("work_life_balance"),
            avg_learning=Avg("learning_opportunity"),
        )

        values = [
            value for value in reputation_score.values()
            if value is not None
        ]

        if values:
            final_score = sum(values) / len(values)
            company.reputation_index = round(
                final_score,
                2
            )
        else:
            company.reputation_index = 0

        company.review_count = reviews.count()
        company.save()