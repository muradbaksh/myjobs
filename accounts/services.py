from django.db import transaction
from .models import CreditTransaction


class CreditService:

    REVIEW_REWARD = 10

    COMPENSATION_VIEW_COST = 5

    @staticmethod
    @transaction.atomic
    def add_credits(user, amount, transaction_type="review_submission", description="", related_object_id=None):
        """
        Add credits to user and log transaction.
        
        Args:
            user: User object
            amount: Number of credits to add
            transaction_type: Type of transaction (review_submission, compensation_submission, etc.)
            description: Optional description of transaction
            related_object_id: Optional reference to related review/compensation ID
        """
        
        balance_before = user.credits
        user.credits += amount
        user.save(update_fields=["credits"])
        
        # Log transaction
        CreditTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=user.credits,
            description=description,
            related_object_id=related_object_id,
            status="completed"
        )

    @staticmethod
    @transaction.atomic
    def deduct_credits(user, amount, transaction_type="benchmark_access", description="", related_object_id=None):
        """
        Deduct credits from user and log transaction.
        Raises ValueError if insufficient credits.
        
        Args:
            user: User object
            amount: Number of credits to deduct
            transaction_type: Type of transaction
            description: Optional description of transaction
            related_object_id: Optional reference to related object ID
        """
        
        if user.credits < amount:
            # Log failed transaction
            CreditTransaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                amount=-amount,
                balance_before=user.credits,
                balance_after=user.credits,
                description=f"Failed: {description}",
                related_object_id=related_object_id,
                status="failed"
            )
            raise ValueError(f"Insufficient credits. Required: {amount}, Available: {user.credits}")

        balance_before = user.credits
        user.credits -= amount
        user.save(update_fields=["credits"])
        
        # Log transaction
        CreditTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=-amount,
            balance_before=balance_before,
            balance_after=user.credits,
            description=description,
            related_object_id=related_object_id,
            status="completed"
        )