from django.db.models import F
from companies.models import Company

class RankingEngine:
    @staticmethod
    def top_companies(limit=10):

        return Company.objects.filter(
            verified=True
        ).order_by(
            "-reputation_index",
            "-review_count"
        )[:limit]

    @staticmethod
    def fastest_growing_companies():

        return Company.objects.annotate(
            growth_score=F("review_count") * F("reputation_index")
        ).order_by(
            "-growth_score"
        )