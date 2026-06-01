from django.db.models import (
    Avg,
    Count,
    Sum,
)

from companies.models import Company

from compensation.models import Compensation

from reviews.models import CompanyReview


class AnalyticsService:

    @staticmethod
    def calculate_employer_reputation_index(company):

        reviews = CompanyReview.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        )

        result = reviews.aggregate(
            reputation=Avg("weighted_score")
        )

        reputation = (
            result["reputation"] or 0
        )

        company.reputation_index = round(
            reputation,
            2
        )

        company.save(
            update_fields=["reputation_index"]
        )

        return company.reputation_index

    @staticmethod
    def get_company_rankings():

        return Company.objects.order_by(
            "-reputation_index",
            "-review_count"
        )

    @staticmethod
    def industry_salary_benchmark(industry):

        return Compensation.objects.filter(
            company__industry=industry,
            is_verified=True,
            is_flagged=False
        ).aggregate(
            average_salary=Avg(
                "total_compensation"
            ),

            total_reports=Count("id"),

            highest_salary=Sum(
                "total_compensation"
            ),
        )