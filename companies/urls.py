from django.urls import path
from .views import CompanyListAPIView, CompanyDetailAPIView


urlpatterns = [
    path("",CompanyListAPIView.as_view(),name="company-list"),
    path("<slug:slug>/",CompanyDetailAPIView.as_view(),name="company-detail"),
]