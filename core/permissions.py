from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in [
                "moderator",
                "admin"
            ]
        )


class IsAdmin(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsAnalyst(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in [
                "analyst",
                "admin"
            ]
        )


class HasSufficientCredits(BasePermission):
    """
    Permission class to check if user has sufficient credits.
    Requires 'required_credits' parameter in view.
    """

    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        required_credits = getattr(view, 'required_credits', 5)
        return request.user.credits >= required_credits