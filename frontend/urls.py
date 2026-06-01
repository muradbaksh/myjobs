from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", HomePageView.as_view(),name='home'),
    path("login/", LoginPageView.as_view(),name='login'),
    path("register/", RegisterPageView.as_view(),name='register'),
    path("profile/",ProfilePageView.as_view(),name="profile"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("companies/", CompanyListPageView.as_view()),
    path("companies/<slug:slug>/",CompanyDetailPageView.as_view()),
    path("review/create/",ReviewFormPageView.as_view()),
    path("reviews/my/", MyReviewsPageView.as_view(), name="my-reviews"),
    path("compensation/create/",CompensationFormPageView.as_view()),
    path("dashboard/",DashboardPageView.as_view()),
    path("benchmark/",BenchmarkPageView.as_view(),name="benchmark"),
    path("about/",AboutPageView.as_view(),name="about"),
    path("contact/",ContactPageView.as_view(),name="contact"),
    path("careers/",CareersPageView.as_view(),name="careers"),
    path("privacy-policy/",PrivacyPolicyPageView.as_view(),name="privacy-policy"),
    path("terms/",TermsPageView.as_view(),name="terms"),
    path("cookies/",CookiesPageView.as_view(),name="cookies"),
        # existing urls...

    path(
        "admin-panel/dashboard/",
        AdminDashboardPageView.as_view(),
        name="admin-dashboard"
    ),

    path(
        "admin-panel/moderation/",
        ModerationPageView.as_view(),
        name="moderation"
    ),

    path(
        "admin-panel/reports/",
        ReportsPageView.as_view(),
        name="reports"
    ),

    path(
        "admin-panel/fraud/",
        FraudDetectionPageView.as_view(),
        name="fraud"
    ),

    path(
        "admin-panel/users/",
        UserManagementPageView.as_view(),
        name="users"
    ),

    path(
        "admin-panel/analytics/",
        AdminAnalyticsPageView.as_view(),
        name="admin-analytics"
    ),

    path(
        "admin-panel/export/",
        ExportPageView.as_view(),
        name="export"
    ),
]