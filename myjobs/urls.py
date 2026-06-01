from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="MYJOBS API",
        default_version='v1',
        description="MYJOBS Backend APIs",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("frontend.urls")),
    path("api/core/", include("core.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/companies/", include("companies.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/compensation/", include("compensation.urls")),
    path("api/analytics/", include("analytics_app.urls")),
    path("swagger/",schema_view.with_ui("swagger",cache_timeout=0)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)