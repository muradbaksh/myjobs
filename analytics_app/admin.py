from django.contrib import admin

# admin.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import CompanyReview
from companies.services import CompanyService

@receiver(post_save, sender=CompanyReview)
def update_company_reputation(sender, instance, **kwargs):
    if instance.is_verified and not instance.is_flagged:
        CompanyService.update_reputation_index(
            instance.company.id
        )