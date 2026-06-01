from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from django.db import models
from .models import User, CreditTransaction
from .tokens import email_verification_token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    CreditTransactionSerializer
)
from rest_framework.generics import RetrieveUpdateAPIView


class RegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        login(request,user)
        return Response(
            {"message": "Registration successful"},
            status=201
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login(request, serializer.user)

        return Response(serializer.validated_data)




class ProfileAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
    


class VerifyEmailAPIView(APIView):

    permission_classes = [AllowAny]
    def get(self, request, user_id, token):

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:

            return Response(
                {"error": "Invalid user"},
                status=400
            )

        if email_verification_token.check_token(
            user,
            token
        ):

            user.is_active = True
            user.is_email_verified = True

            user.save()

            return Response({
                "message":
                    "Email verified successfully"
            })

        return Response(
            {
                "error": "Invalid token"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    



class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        logout(request)

        return redirect("/")

    def post(self, request):

        logout(request)

        return Response({
            "message": "Logout successful"
        })


class CreditHistoryAPIView(ListAPIView):
    """
    View credit transaction history for authenticated user.
    Paginated list of all credit operations.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = CreditTransactionSerializer
    pagination_class = None
    
    def get_queryset(self):
        return CreditTransaction.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class CreditBalanceAPIView(APIView):
    """
    Get current credit balance and statistics for user.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        transactions = CreditTransaction.objects.filter(
            user=user
        )
        
        total_earned = transactions.filter(
            amount__gt=0,
            status="completed"
        ).aggregate(total=models.Sum("amount"))["total"] or 0
        
        total_spent = abs(transactions.filter(
            amount__lt=0,
            status="completed"
        ).aggregate(total=models.Sum("amount"))["total"] or 0)
        
        return Response({
            "current_balance": user.credits,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "transaction_count": transactions.count(),
        })
