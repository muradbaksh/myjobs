from .models import CompanyReview


def get_company_reviews(company):

    return CompanyReview.objects.filter(
        company=company,
        is_verified=True,
        is_flagged=False
    )


def get_user_reviews(user):

    return CompanyReview.objects.filter(
        user=user
    )