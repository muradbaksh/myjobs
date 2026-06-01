from rest_framework import serializers

from companies.models import Company


class CompanyRankingSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Company

        fields = [
            "id",
            "name",
            "industry",
            "reputation_index",
            "review_count",
        ]