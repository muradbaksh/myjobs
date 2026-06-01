from rest_framework.generics import (
    CreateAPIView,
    ListAPIView
)
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .models import Compensation
from .serializers import (
    CompensationCreateSerializer,
    CompensationListSerializer
)
from .analytics import CompensationAnalytics
from .services import CompensationService
from core.throttles import (
    CompensationSubmissionThrottle,
    AnalyticsThrottle
)
from core.permissions import HasSufficientCredits


class CompensationCreateAPIView(CreateAPIView):
    serializer_class = (
        CompensationCreateSerializer
    )
    permission_classes = [IsAuthenticated]
    throttle_classes = [CompensationSubmissionThrottle]


class UserCompensationListAPIView(ListAPIView):

    serializer_class = (
        CompensationListSerializer
    )

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Compensation.objects.filter(
            user=self.request.user
        )


class CompensationBenchmarkAPIView(APIView):

    permission_classes = [IsAuthenticated, HasSufficientCredits]
    throttle_classes = [AnalyticsThrottle]
    required_credits = 5
    
    def get(self, request):
        company_id = request.GET.get("company")
        job_title = request.GET.get("job_title")
        
        if not company_id or not job_title:
            return Response(
                {
                    "error": "company and job_title parameters are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = (
            f"benchmark_{company_id}_{job_title}"
        )
        cached_data = cache.get(cache_key)

        if cached_data:
            try:
                CompensationService.deduct_benchmark_credits(
                    request.user
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            return Response(cached_data)
        

        queryset = Compensation.objects.filter(
            company_id=company_id,
            normalized_job_title=job_title,
            is_verified=True,
            is_flagged=False
        )

        # K-anonymity protection: minimum 5 data points required
        if queryset.count() < 5:

            return Response(
                {
                    "message":
                        "Not enough data available for this role"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # deduct credits
        try:
            CompensationService.deduct_benchmark_credits(
                request.user
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        analytics = (
            CompensationAnalytics.calculate_percentiles(
                queryset
            )
        )

        response_data = {
            "job_title": job_title,
            "company_id": company_id,
            "analytics": analytics,
        }

        cache.set(
            cache_key,
            response_data,
            timeout=60 * 15
        )

        return Response(response_data)