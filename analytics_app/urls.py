from django.urls import path

from .views import (
    PlatformOverviewAPIView,
    CompanyRankingAPIView,
    IndustryBenchmarkAPIView,
    ExecutiveReportAPIView,
    FraudDetectionAPIView,
    ModerationQueueAPIView,
    VerifyReviewAPIView,
    VerifyCompensationAPIView,
    ExportReviewsCSVAPIView,
    ExportCompensationExcelAPIView,
    AdminDashboardAPIView,
)

urlpatterns = [
    path("platform-overview/",PlatformOverviewAPIView.as_view(),name="platform-overview"),
    path("company-rankings/",CompanyRankingAPIView.as_view(),name="company-rankings"),
    path("industry-benchmark/",IndustryBenchmarkAPIView.as_view(),name="industry-benchmark"),
    path("executive-report/",ExecutiveReportAPIView.as_view(),name="executive-report"),
    path("fraud-detection/",FraudDetectionAPIView.as_view(),name="fraud-detection"),
    path("moderation-queue/",ModerationQueueAPIView.as_view(),name="moderation-queue"),
    path("verify-review/<int:review_id>/",VerifyReviewAPIView.as_view(),name="verify-review"),
    path("verify-compensation/<int:compensation_id>/",VerifyCompensationAPIView.as_view(),name="verify-compensation"),

    path(
    "admin/dashboard/",
    AdminDashboardAPIView.as_view(),
    name="admin-dashboard"
),

path(
    "export/reviews/csv/",
    ExportReviewsCSVAPIView.as_view(),
    name="export-reviews-csv"
),

path(
    "export/compensation/excel/",
    ExportCompensationExcelAPIView.as_view(),
    name="export-compensation-excel"
),
]