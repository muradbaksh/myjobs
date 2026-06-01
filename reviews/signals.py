from django.db.models.signals import post_save

from django.dispatch import receiver

from .models import CompanyReview


@receiver(post_save, sender=CompanyReview)
def review_post_save(sender, instance, created, **kwargs):

    if created:
        pass