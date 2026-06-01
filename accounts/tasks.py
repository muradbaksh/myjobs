from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import User
from .tokens import email_verification_token
from django.conf import settings


@shared_task
def send_verification_email(user_id):

    user = User.objects.get(id=user_id)
    token = email_verification_token.make_token(user)

    verification_link = (
        f"{settings.FRONTEND_URL}"
        f"/api/accounts/verify-email/{user.id}/{token}/"
    )

    send_mail(
        subject="Verify Your MYJOBS Account",

        message=f"""
                Hello {user.full_name},

                Please verify your account:

                {verification_link}

                Thank you.
                        """,

        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return "Verification Email Sent"