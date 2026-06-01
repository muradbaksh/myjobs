from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    ProfileAPIView,
    VerifyEmailAPIView,
    LogoutAPIView,
    CreditHistoryAPIView,
    CreditBalanceAPIView
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("credits/history/", CreditHistoryAPIView.as_view(), name="credit-history"),
    path("credits/balance/", CreditBalanceAPIView.as_view(), name="credit-balance"),
]