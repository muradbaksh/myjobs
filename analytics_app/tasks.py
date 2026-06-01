from celery import shared_task

from compensation.models import Compensation


@shared_task
def refresh_salary_benchmarks():

    total = Compensation.objects.count()

    return (
        f"Salary benchmark "
        f"refresh complete: {total}"
    )