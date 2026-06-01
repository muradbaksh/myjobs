from rest_framework import serializers

from .models import Compensation

from .validators import (
    validate_salary,
    validate_fairness_rating
)

from .services import CompensationService


class CompensationCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Compensation

        exclude = [
            "user",
            "normalized_job_title",
            "total_compensation",
            "is_verified",
            "is_flagged",
            "moderation_note",
        ]

    def validate(self, attrs):

        validate_salary(attrs["base_salary"])

        validate_fairness_rating(
            attrs["market_fairness_rating"]
        )

        return attrs

    def create(self, validated_data):

        user = self.context["request"].user

        compensation = Compensation.objects.create(
            user=user,
            **validated_data
        )

        CompensationService.process_compensation_creation(
            compensation
        )

        return compensation


class CompensationListSerializer(
    serializers.ModelSerializer
):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:

        model = Compensation

        fields = [
            "id",
            "company_name",
            "normalized_job_title",
            "experience_level",
            "location",
            "total_compensation",
        ]