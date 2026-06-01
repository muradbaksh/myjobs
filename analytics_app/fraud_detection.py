from reviews.models import CompanyReview

from compensation.models import Compensation


class FraudDetectionService:

    @staticmethod
    def detect_suspicious_reviews():

        suspicious_reviews = []

        reviews = CompanyReview.objects.all()

        for review in reviews:

            if review.weighted_score == 5:

                suspicious_reviews.append(
                    review.id
                )

        return suspicious_reviews

    @staticmethod
    def detect_salary_outliers():

        suspicious_compensations = []

        compensations = Compensation.objects.filter(
            total_compensation__gt=1000000
        )

        for compensation in compensations:

            suspicious_compensations.append(
                compensation.id
            )

        return suspicious_compensations