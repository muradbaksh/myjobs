from .models import Company


def get_companies():

    return Company.objects.all()


def get_verified_companies():

    return Company.objects.filter(
        verified=True
    )


def get_company_by_slug(slug):

    return Company.objects.filter(
        slug=slug
    ).first()