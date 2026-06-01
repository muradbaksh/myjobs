from django.contrib.auth import get_user_model

from companies.models import Company
from reviews.models import CompanyReview
from compensation.models import Compensation


User = get_user_model()


class AdminDashboardService:

    @staticmethod
    def get_dashboard_metrics():

        return {
            "total_users":
                User.objects.count(),

            "total_companies":
                Company.objects.count(),

            "total_reviews":
                CompanyReview.objects.count(),

            "total_compensations":
                Compensation.objects.count(),

            "flagged_reviews":
                CompanyReview.objects.filter(
                    is_flagged=True
                ).count(),

            "flagged_compensations":
                Compensation.objects.filter(
                    is_flagged=True
                ).count(),

            "pending_review_verification":
                CompanyReview.objects.filter(
                    is_verified=False
                ).count(),

            "pending_compensation_verification":
                Compensation.objects.filter(
                    is_verified=False
                ).count(),

            "total_credits_issued": sum(
                User.objects.values_list(
                    "credits",
                    flat=True
                )
            )
        }