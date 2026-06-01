from rest_framework import serializers

from .models import CompanyReview

from .validators import validate_rating

from reviews.services import ReviewService


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:

        model = CompanyReview

        exclude = [
            "user",
            "anonymous_reference",
            "weighted_score",
            "is_verified",
            "is_flagged",
            "moderation_note",
        ]

    def validate(self, attrs):

        rating_fields = [
            "company_brand_value",
            "work_environment",
            "career_growth",
            "salary_satisfaction",
            "fringe_benefits",
            "job_security",
            "employee_respect",
            "management_quality",
            "work_life_balance",
            "learning_opportunity",
        ]

        for field in rating_fields:

            validate_rating(attrs[field])

        return attrs

    def create(self, validated_data):

        user = self.context["request"].user

        review = CompanyReview.objects.create(
            user=user,
            **validated_data
        )

        ReviewService.process_review_creation(
            review
        )

        return review


class ReviewListSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:

        model = CompanyReview

        fields = [
            "id",
            "company_name",
            "weighted_score",
            "overall_recommendation",
            "created_at",
        ]