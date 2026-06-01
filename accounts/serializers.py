from rest_framework import serializers
from .tasks import send_verification_email
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, CreditTransaction


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User

        fields = [
            "email",
            "username",
            "full_name",
            "password",
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_active=True,
            is_email_verified=True,
            **validated_data
        )    
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        self.user = user
        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "credits": user.credits,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }



class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ["password"]
        read_only_fields = [
            "id",
            "credits",
            "role",
            "is_staff",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CreditTransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CreditTransaction
        
        fields = [
            "id",
            "transaction_type",
            "amount",
            "status",
            "balance_before",
            "balance_after",
            "description",
            "related_object_id",
            "created_at",
        ]
        
        read_only_fields = [
            "id",
            "created_at",
            "balance_before",
            "balance_after",
        ]