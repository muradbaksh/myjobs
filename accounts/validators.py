from django.core.exceptions import ValidationError


PROFESSIONAL_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
]


def validate_professional_email(email):

    domain = email.split("@")[-1]

    if domain in PROFESSIONAL_EMAIL_DOMAINS:
        raise ValidationError(
            "Use professional company email"
        )