from django.contrib import admin
from .models import User, CreditTransaction

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "full_name",
        "credits",
        "is_verified_professional",
        "is_staff",
    )

    search_fields = (
        "email",
        "username",
    )

    list_filter = (
        "is_verified_professional",
        "is_staff",
    )

    readonly_fields = (
        "anonymous_identity",
    )


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    
    list_display = (
        "user",
        "transaction_type",
        "amount",
        "balance_before",
        "balance_after",
        "status",
        "created_at",
    )
    
    list_filter = (
        "transaction_type",
        "status",
        "created_at",
    )
    
    search_fields = (
        "user__email",
        "user__username",
        "related_object_id",
    )
    
    readonly_fields = (
        "user",
        "balance_before",
        "balance_after",
        "created_at",
    )
    
    def has_delete_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False