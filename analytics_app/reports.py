from django.db.models import (
    Avg,
    Count,
)

from compensation.models import Compensation


class ReportingService:

    @staticmethod
    def executive_salary_report():

        return Compensation.objects.values(
            "normalized_job_title"
        ).annotate(
            average_salary=Avg(
                "total_compensation"
            ),

            total_reports=Count("id")
        ).order_by(
            "-average_salary"
        )