from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Company
from .serializers import (
    CompanyListSerializer,
    CompanyDetailSerializer
)
from .filters import CompanyFilter


class CompanyListAPIView(ListAPIView):

    serializer_class = CompanyListSerializer

    permission_classes = [AllowAny]

    queryset = Company.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = CompanyFilter

    search_fields = [
        "name",
        "industry",
    ]

    ordering_fields = [
        "review_count",
        "reputation_index",
    ]


class CompanyDetailAPIView(RetrieveAPIView):

    serializer_class = CompanyDetailSerializer

    permission_classes = [AllowAny]

    lookup_field = "slug"

    queryset = Company.objects.all()