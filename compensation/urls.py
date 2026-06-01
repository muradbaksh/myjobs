from django.urls import path

from .views import (
    CompensationCreateAPIView,
    UserCompensationListAPIView,
    CompensationBenchmarkAPIView,
)

urlpatterns = [
    path("create/",CompensationCreateAPIView.as_view(),name="compensation-create"),
    path("my-compensations/",UserCompensationListAPIView.as_view(),name="my-compensations"),
    path("benchmark/",CompensationBenchmarkAPIView.as_view(),name="benchmark"),
]