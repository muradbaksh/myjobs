from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from core.permissions import IsModerator, IsAdmin
from reviews.models import CompanyReview
from compensation.models import Compensation
from django.core.cache import cache
from .services import AnalyticsService
from .dashboard import DashboardAnalytics
from .ranking import RankingEngine
from .reports import ReportingService
from .fraud_detection import FraudDetectionService
from .serializers import CompanyRankingSerializer
from .export import ExportService
from .admin_dashboard import AdminDashboardService



class PlatformOverviewAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        cache_key = "platform_overview"

        data = cache.get(cache_key)

        if not data:

            data = (
                DashboardAnalytics.platform_overview()
            )

            cache.set(
                cache_key,
                data,
                timeout=60 * 10
            )

        return Response(data)


class CompanyRankingAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        companies = RankingEngine.top_companies()

        serializer = (
            CompanyRankingSerializer(
                companies,
                many=True
            )
        )

        return Response(serializer.data)


class IndustryBenchmarkAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        industry = request.GET.get("industry")

        cache_key = (
            f"industry_benchmark_{industry}"
        )

        data = cache.get(cache_key)

        if not data:

            data = (
                AnalyticsService.industry_salary_benchmark(
                    industry
                )
            )

            cache.set(
                cache_key,
                data,
                timeout=60 * 15
            )

        return Response(data)


class ExecutiveReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = (
            ReportingService.executive_salary_report()
        )

        return Response(report)


class FraudDetectionAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        suspicious_reviews = (
            FraudDetectionService.detect_suspicious_reviews()
        )

        suspicious_compensations = (
            FraudDetectionService.detect_salary_outliers()
        )

        return Response({
            "suspicious_reviews":
                suspicious_reviews,

            "suspicious_compensations":
                suspicious_compensations,
        })


class ModerationQueueAPIView(APIView):

    permission_classes = [IsModerator]

    def get(self, request):

        reviews = CompanyReview.objects.filter(
            is_flagged=True
        )

        compensations = Compensation.objects.filter(
            is_flagged=True
        )

        return Response({
            "flagged_reviews":
                reviews.count(),

            "flagged_compensations":
                compensations.count(),
        })


class VerifyReviewAPIView(APIView):

    permission_classes = [IsModerator]

    def post(self, request, review_id):

        try:

            review = CompanyReview.objects.get(
                id=review_id
            )

            review.is_verified = True

            review.save()

            return Response({
                "message":
                    "Review verified"
            })

        except CompanyReview.DoesNotExist:

            return Response({
                "error":
                    "Review not found"
            })


class VerifyCompensationAPIView(APIView):

    permission_classes = [IsModerator]

    def post(self, request, compensation_id):

        try:

            compensation = Compensation.objects.get(
                id=compensation_id
            )

            compensation.is_verified = True

            compensation.save()

            return Response({
                "message":
                    "Compensation verified"
            })

        except Compensation.DoesNotExist:

            return Response({
                "error":
                    "Compensation not found"
            })
        

# Admin dashboard 
class ExportReviewsCSVAPIView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        return (
            ExportService.export_reviews_csv()
        )


class ExportCompensationExcelAPIView(
    APIView
):

    permission_classes = [IsAdmin]

    def get(self, request):

        return (
            ExportService.export_compensation_excel()
        )


class AdminDashboardAPIView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        data = (
            AdminDashboardService
            .get_dashboard_metrics()
        )

        return Response(data)