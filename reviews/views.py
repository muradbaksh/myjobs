from rest_framework.generics import (
    CreateAPIView,
    ListAPIView
)
from rest_framework.permissions import (
    IsAuthenticated
)
from .models import CompanyReview
from .serializers import (
    ReviewCreateSerializer,
    ReviewListSerializer,
)
from core.throttles import (
    ReviewSubmissionThrottle
)


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewSubmissionThrottle]


class UserReviewListAPIView(ListAPIView):
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return CompanyReview.objects.filter(
            user=self.request.user
        )