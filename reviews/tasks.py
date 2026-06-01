from celery import shared_task
from companies.models import Company
from celery import shared_task

# future background review tasks here


@shared_task
def recalculate_company_reputation(
    company_id
):

    try:
        company = Company.objects.get(
            id=company_id
        )

        reviews = company.reviews.all()

        if not reviews.exists():
            return

        reputation_score = (
            sum(
                review.weighted_score
                for review in reviews
            )
            / reviews.count()
        )

        company.reputation_index = (
            round(reputation_score, 2)
        )

        company.save()

        return (
            f"Updated reputation "
            f"for {company.name}"
        )

    except Company.DoesNotExist:

        return "Company not found"
    



@shared_task
def fraud_detection_scan(review_id):

    from reviews.models import CompanyReview

    try:

        review = CompanyReview.objects.get(
            id=review_id
        )

        suspicious_keywords = [
            "fake",
            "scam",
            "fraud",
        ]

        review_text = (
            review.review_text.lower()
        )

        if any(
            keyword in review_text
            for keyword in suspicious_keywords
        ):

            review.is_flagged = True

            review.save()

            return "Flagged"

        return "Clean"

    except CompanyReview.DoesNotExist:

        return "Review not found"