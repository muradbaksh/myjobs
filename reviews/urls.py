from django.urls import path

from .views import (
    ReviewCreateAPIView,
    UserReviewListAPIView,
)

urlpatterns = [
    path("create/",ReviewCreateAPIView.as_view(),name="review-create"),
    path("my-reviews/",UserReviewListAPIView.as_view(),name="my-reviews"),
]