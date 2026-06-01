from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home/index.html"


class LoginPageView(TemplateView):
    template_name = "accounts/login.html"


class RegisterPageView(TemplateView):
    template_name = "accounts/register.html"

class ProfilePageView(TemplateView):
    template_name = "accounts/profile.html"


class CompanyListPageView(TemplateView):
    template_name = "companies/company_list.html"


class CompanyDetailPageView(TemplateView):
    template_name = "companies/company_detail.html"


class ReviewFormPageView(TemplateView):
    template_name = "reviews/review_form.html"


class MyReviewsPageView(TemplateView):
    template_name = "reviews/my_reviews.html"


class CompensationFormPageView(TemplateView):
    template_name = "compensation/compensation_form.html"


class DashboardPageView(TemplateView):
    template_name = "analytics/dashboard.html"



# admin
class AdminDashboardPageView(TemplateView):
    template_name = "admin/dashboard.html"


class ModerationPageView(TemplateView):
    template_name = "admin/moderation.html"


class ReportsPageView(TemplateView):
    template_name = "admin/reports.html"


class FraudDetectionPageView(TemplateView):
    template_name = "admin/fraud.html"


class UserManagementPageView(TemplateView):
    template_name = "admin/users.html"


class AdminAnalyticsPageView(TemplateView):
    template_name = "admin/analytics.html"


class ExportPageView(TemplateView):
    template_name = "admin/export.html"


class BenchmarkPageView(TemplateView):
    template_name = "compensation/benchmark.html"



class AboutPageView(TemplateView):
    template_name = "partials/about.html"


class ContactPageView(TemplateView):
    template_name = "partials/contact.html"


class CareersPageView(TemplateView):
    template_name = "partials/careers.html"


class PrivacyPolicyPageView(TemplateView):
    template_name = "partials/privacy_policy.html"


class TermsPageView(TemplateView):
    template_name = "partials/terms.html"


class CookiesPageView(TemplateView):
    template_name = "partials/cookies.html"