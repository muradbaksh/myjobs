import numpy as np

from compensation.models import Compensation


class CompensationAnalytics:

    K_ANONYMITY_THRESHOLD = 5

    @staticmethod
    def calculate_percentiles(queryset):

        salaries = list(
            queryset.values_list(
                "total_compensation",
                flat=True
            )
        )

        if len(salaries) < 5:
            return None

        salaries = sorted([
            float(salary)
            for salary in salaries
        ])

        return {
            "p25": round(
                np.percentile(salaries, 25),
                2
            ),

            "p50": round(
                np.percentile(salaries, 50),
                2
            ),

            "p75": round(
                np.percentile(salaries, 75),
                2
            ),
        }

    @staticmethod
    def detect_outlier(total_compensation, queryset):

        salaries = list(
            queryset.values_list(
                "total_compensation",
                flat=True
            )
        )

        if len(salaries) < 5:
            return False

        salaries = np.array([
            float(s)
            for s in salaries
        ])

        mean = salaries.mean()

        std = salaries.std()

        if std == 0:
            return False

        z_score = (
            abs(float(total_compensation) - mean)
            / std
        )

        return z_score > 3