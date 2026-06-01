from rest_framework import serializers

from .models import Company


class CompanyListSerializer(serializers.ModelSerializer):

    class Meta:

        model = Company

        fields = [
            "id",
            "name",
            "slug",
            "company_type",
            "industry",
            "manpower_size",
            "verified",
            "review_count",
            "reputation_index",
        ]


class CompanyDetailSerializer(serializers.ModelSerializer):

    class Meta:

        model = Company

        fields = "__all__"