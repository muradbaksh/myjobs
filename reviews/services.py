import uuid

from django.db import transaction

from django.db.models import Avg

from companies.services import CompanyService

from accounts.services import CreditService


class ReviewService:

    REVIEW_REWARD = 10

    @staticmethod
    def generate_anonymous_reference():

        return uuid.uuid4()

    @staticmethod
    def calculate_weighted_score(review):

        ratings = [
            review.company_brand_value,
            review.work_environment,
            review.career_growth,
            review.salary_satisfaction,
            review.fringe_benefits,
            review.job_security,
            review.employee_respect,
            review.management_quality,
            review.work_life_balance,
            review.learning_opportunity,
        ]

        return round(sum(ratings) / len(ratings), 2)

    @staticmethod
    @transaction.atomic
    def process_review_creation(review):

        # weighted score
        review.weighted_score = (
            ReviewService.calculate_weighted_score(review)
        )

        # anonymous reference
        review.anonymous_reference = (
            ReviewService.generate_anonymous_reference()
        )

        review.save()

        # reward credits with transaction logging
        CreditService.add_credits(
            review.user,
            ReviewService.REVIEW_REWARD,
            transaction_type="review_submission",
            description=f"Review submitted for {review.company.name}",
            related_object_id=str(review.id)
        )

        # update company reputation
        CompanyService.update_reputation_index(
            review.company.id
        )