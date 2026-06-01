from rest_framework.exceptions import ValidationError


def validate_salary(value):

    if value <= 0:
        raise ValidationError(
            "Salary must be greater than 0"
        )


def validate_fairness_rating(value):

    if value < 1 or value > 5:
        raise ValidationError(
            "Fairness rating must be between 1 and 5"
        )