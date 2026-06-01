from django.db.models import (
    Avg,
    Count,
)

from companies.models import Company

from compensation.models import Compensation

from reviews.models import CompanyReview


class DashboardAnalytics:

    @staticmethod
    def platform_overview():

        return {
            "total_companies":
                Company.objects.count(),

            "total_reviews":
                CompanyReview.objects.count(),

            "total_compensations":
                Compensation.objects.count(),

            "average_platform_reputation":
                Company.objects.aggregate(
                    Avg("reputation_index")
                )["reputation_index__avg"],
        }

    @staticmethod
    def top_industries():

        return Company.objects.values(
            "industry"
        ).annotate(
            total=Count("id")
        ).order_by("-total")