from .models import Compensation


def get_company_compensations(company):

    return Compensation.objects.filter(
        company=company,
        is_verified=True,
        is_flagged=False
    )


def get_job_title_compensations(job_title):

    return Compensation.objects.filter(
        normalized_job_title=job_title,
        is_verified=True,
        is_flagged=False
    )