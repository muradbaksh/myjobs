from companies.models import Company


def get_verified_companies():

    return Company.objects.filter(
        verified=True
    )


def get_top_ranked_companies():

    return Company.objects.order_by(
        "-reputation_index"
    )