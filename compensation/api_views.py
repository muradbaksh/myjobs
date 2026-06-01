"""
Phase 3 REST APIs for MYJOBS Compensation Platform

This module implements comprehensive REST API endpoints for salary analytics,
company statistics, and compensation data insights. All endpoints include
proper error handling, caching strategies, and permission controls.
"""

from django.db.models import Avg, Count, Q, Max, Min
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils.text import slugify

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta

from companies.models import Company
from reviews.models import CompanyReview
from .models import Compensation
from .analytics import CompensationAnalytics
from .services import CompensationService
from .serializers import (
    CompensationCreateSerializer,
    CompensationListSerializer
)
from core.throttles import AnalyticsThrottle
from core.permissions import IsModerator


# ==================== Pagination Classes ====================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for list endpoints (20 results per page)."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CompensationResultsSetPagination(PageNumberPagination):
    """Pagination for compensation list endpoints (15 results per page)."""
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==================== Serializers ====================

class CompanyDetailSerializer(serializers.Serializer):
    """Serializer for detailed company profile with aggregated statistics."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    company_type = serializers.CharField(read_only=True)
    industry = serializers.CharField(read_only=True)
    reputation_index = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    compensation_count = serializers.IntegerField(read_only=True)
    avg_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    verified = serializers.BooleanField(read_only=True)
    headquarters = serializers.CharField(read_only=True)
    website = serializers.URLField(read_only=True, allow_null=True)
    logo = serializers.ImageField(read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    top_3_reviews_summary = serializers.SerializerMethodField()

    def get_top_3_reviews_summary(self, obj):
        """Get top 3 reviews by weighted score."""
        top_reviews = CompanyReview.objects.filter(
            company=obj,
            is_flagged=False,
            is_verified=True
        ).order_by('-weighted_score')[:3]

        return [
            {
                'rating': review.weighted_score,
                'recommendation': review.overall_recommendation,
                'text': review.review_text[:200] if review.review_text else None,
                'created_at': review.created_at.isoformat()
            }
            for review in top_reviews
        ]


class CompanyReviewSummarySerializer(serializers.Serializer):
    """Serializer for review summaries without user identity."""
    id = serializers.IntegerField(read_only=True)
    weighted_score = serializers.FloatField(read_only=True)
    overall_recommendation = serializers.CharField(read_only=True)
    company_brand_value = serializers.IntegerField(read_only=True)
    work_environment = serializers.IntegerField(read_only=True)
    career_growth = serializers.IntegerField(read_only=True)
    salary_satisfaction = serializers.IntegerField(read_only=True)
    fringe_benefits = serializers.IntegerField(read_only=True)
    job_security = serializers.IntegerField(read_only=True)
    employee_respect = serializers.IntegerField(read_only=True)
    management_quality = serializers.IntegerField(read_only=True)
    work_life_balance = serializers.IntegerField(read_only=True)
    learning_opportunity = serializers.IntegerField(read_only=True)
    review_text = serializers.CharField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


class CompanyStatisticsSerializer(serializers.Serializer):
    """Serializer for aggregate company statistics."""
    company_id = serializers.IntegerField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    average_overall_rating = serializers.FloatField(read_only=True)
    recommendation_breakdown = serializers.DictField(read_only=True)
    ratings_by_category = serializers.DictField(read_only=True)
    total_compensation_records = serializers.IntegerField(read_only=True)
    avg_total_compensation = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )


class SalaryTrendSerializer(serializers.Serializer):
    """Serializer for salary trends over time."""
    job_title = serializers.CharField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    period = serializers.CharField(read_only=True)
    yearly_data = serializers.ListField(read_only=True)
    growth_percentage = serializers.FloatField(read_only=True)
    trend_direction = serializers.CharField(read_only=True)


class LocationSalarySerializer(serializers.Serializer):
    """Serializer for location-based salary comparison."""
    location = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    avg_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    median_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    salary_range = serializers.DictField(read_only=True)
    sample_size = serializers.IntegerField(read_only=True)


class IndustrySalaryBenchmarkSerializer(serializers.Serializer):
    """Serializer for industry-wide salary benchmarks."""
    industry = serializers.CharField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    avg_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    median_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p25 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p75 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    sample_size = serializers.IntegerField(read_only=True)


class JobTitleAutocompleteSerializer(serializers.Serializer):
    """Serializer for job title autocomplete."""
    title = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)


class PercentileDataSerializer(serializers.Serializer):
    """Serializer for percentile salary breakdown."""
    job_title = serializers.CharField(read_only=True)
    company = serializers.CharField(read_only=True, allow_null=True)
    location = serializers.CharField(read_only=True, allow_null=True)
    experience_level = serializers.CharField(read_only=True, allow_null=True)
    p10 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p25 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p50 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p75 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p90 = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    sample_size = serializers.IntegerField(read_only=True)


class PlatformOverviewSerializer(serializers.Serializer):
    """Serializer for platform statistics overview."""
    total_reviews = serializers.IntegerField(read_only=True)
    total_companies = serializers.IntegerField(read_only=True)
    total_compensation_records = serializers.IntegerField(read_only=True)
    verified_companies = serializers.IntegerField(read_only=True)
    average_company_rating = serializers.FloatField(read_only=True)
    recent_activity = serializers.ListField(read_only=True)


class CompanyRankingSerializer(serializers.Serializer):
    """Serializer for ranked companies."""
    rank = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    industry = serializers.CharField(read_only=True)
    reputation_index = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    avg_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    score = serializers.FloatField(read_only=True)


# ==================== API Views ====================

class CompanyDetailAPIView(APIView):
    """
    API view for retrieving detailed company profile with aggregated statistics.

    GET: Returns company information with reputation index, review count,
         average salary, and top 3 reviews summary.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 1 hour
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve detailed company profile.

        Query Parameters:
            company_id: Company identifier (required)

        Returns:
            - Company profile data with aggregated statistics
            - Top 3 reviews summary
            - Reputation metrics

        Errors:
            - 400: Missing or invalid company_id
            - 404: Company not found
        """
        company_id = request.GET.get('company_id')

        if not company_id:
            return Response(
                {'error': 'company_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'company_detail_{company_id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        avg_salary = Compensation.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        ).aggregate(avg=Avg('total_compensation'))['avg'] or 0

        data = {
            'id': company.id,
            'name': company.name,
            'company_type': company.company_type,
            'industry': company.industry,
            'reputation_index': company.reputation_index,
            'review_count': company.review_count,
            'compensation_count': company.compensation_count,
            'avg_salary': avg_salary,
            'verified': company.verified,
            'headquarters': company.headquarters,
            'website': company.website,
            'logo': company.logo.url if company.logo else None,
            'description': company.description,
            'top_3_reviews_summary': [
                {
                    'rating': float(review.weighted_score),
                    'recommendation': review.overall_recommendation,
                    'text': review.review_text[:200] if review.review_text else None,
                    'created_at': review.created_at.isoformat()
                }
                for review in CompanyReview.objects.filter(
                    company=company,
                    is_flagged=False,
                    is_verified=True
                ).order_by('-weighted_score')[:3]
            ]
        }

        cache.set(cache_key, data, timeout=60 * 60)  # 1 hour
        return Response(data)


class CompanyReviewsAPIView(ListAPIView):
    """
    API view for retrieving paginated company reviews without user identity.

    GET: Returns list of company reviews with sorting and pagination.

    Permissions: AllowAny
    Pagination: StandardResultsSetPagination
    Throttling: AnalyticsThrottle
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [AnalyticsThrottle]

    def get_queryset(self):
        """
        Retrieve company reviews filtered and sorted.

        Query Parameters:
            company_id: Filter by company (required)
            sort: Sort order - 'newest' or 'rating' (default: newest)

        Returns:
            QuerySet of filtered and sorted reviews
        """
        company_id = self.request.GET.get('company_id')

        if not company_id:
            return CompanyReview.objects.none()

        queryset = CompanyReview.objects.filter(
            company_id=company_id,
            is_flagged=False,
            is_verified=True
        )

        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'rating':
            queryset = queryset.order_by('-weighted_score')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get(self, request, *args, **kwargs):
        """
        Get reviews for a company.

        Errors:
            - 400: Missing company_id parameter
        """
        if not request.GET.get('company_id'):
            return Response(
                {'error': 'company_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        return CompanyReviewSummarySerializer


class CompanyStatisticsAPIView(APIView):
    """
    API view for retrieving aggregate review statistics by company.

    GET: Returns average ratings per field, recommendation percentages,
         and distribution data.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 1 hour
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve aggregate company statistics.

        Query Parameters:
            company_id: Company identifier (required)

        Returns:
            - Average ratings for all 10 rating categories
            - Recommendation breakdown percentages
            - Total review and compensation counts

        Errors:
            - 400: Missing company_id
            - 404: Company not found
        """
        company_id = request.GET.get('company_id')

        if not company_id:
            return Response(
                {'error': 'company_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'company_stats_{company_id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        reviews = CompanyReview.objects.filter(
            company=company,
            is_flagged=False,
            is_verified=True
        )

        stats = reviews.aggregate(
            avg_brand=Avg('company_brand_value'),
            avg_environment=Avg('work_environment'),
            avg_growth=Avg('career_growth'),
            avg_salary=Avg('salary_satisfaction'),
            avg_benefits=Avg('fringe_benefits'),
            avg_security=Avg('job_security'),
            avg_respect=Avg('employee_respect'),
            avg_management=Avg('management_quality'),
            avg_balance=Avg('work_life_balance'),
            avg_learning=Avg('learning_opportunity'),
            overall_avg=Avg('weighted_score')
        )

        recommendation_stats = reviews.values('overall_recommendation').annotate(
            count=Count('id')
        )

        total_reviews = reviews.count()
        recommendation_breakdown = {
            'yes': 0,
            'neutral': 0,
            'no': 0
        }

        for rec in recommendation_stats:
            percentage = (rec['count'] / total_reviews * 100) if total_reviews > 0 else 0
            recommendation_breakdown[rec['overall_recommendation']] = round(percentage, 2)

        compensation_stats = Compensation.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        ).aggregate(
            avg_compensation=Avg('total_compensation'),
            total_count=Count('id')
        )

        data = {
            'company_id': company.id,
            'company_name': company.name,
            'total_reviews': total_reviews,
            'average_overall_rating': round(float(stats['overall_avg'] or 0), 2),
            'recommendation_breakdown': recommendation_breakdown,
            'ratings_by_category': {
                'company_brand_value': round(float(stats['avg_brand'] or 0), 2),
                'work_environment': round(float(stats['avg_environment'] or 0), 2),
                'career_growth': round(float(stats['avg_growth'] or 0), 2),
                'salary_satisfaction': round(float(stats['avg_salary'] or 0), 2),
                'fringe_benefits': round(float(stats['avg_benefits'] or 0), 2),
                'job_security': round(float(stats['avg_security'] or 0), 2),
                'employee_respect': round(float(stats['avg_respect'] or 0), 2),
                'management_quality': round(float(stats['avg_management'] or 0), 2),
                'work_life_balance': round(float(stats['avg_balance'] or 0), 2),
                'learning_opportunity': round(float(stats['avg_learning'] or 0), 2),
            },
            'total_compensation_records': compensation_stats['total_count'],
            'avg_total_compensation': compensation_stats['avg_compensation'] or 0
        }

        cache.set(cache_key, data, timeout=60 * 60)  # 1 hour
        return Response(data)


class SalaryTrendAPIView(APIView):
    """
    API view for retrieving salary trends over time.

    GET: Returns yearly average salaries, growth percentage, and trend direction.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 24 hours
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve salary trends for a job title in a company.

        Query Parameters:
            company_id: Company identifier (required)
            job_title: Job title (required)
            years: Number of years to analyze - 1, 3, or 5 (default: 5)

        Returns:
            - Yearly average salary data
            - Growth percentage over period
            - Trend direction (upward/downward/stable)

        Errors:
            - 400: Missing required parameters
            - 404: Company not found
        """
        company_id = request.GET.get('company_id')
        job_title = request.GET.get('job_title')
        years = int(request.GET.get('years', 5))

        if not company_id or not job_title:
            return Response(
                {'error': 'company_id and job_title parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if years not in [1, 3, 5]:
            years = 5

        cache_key = f'salary_trend_{company_id}_{slugify(job_title)}_{years}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cutoff_date = datetime.now() - timedelta(days=365 * years)

        compensations = Compensation.objects.filter(
            company=company,
            normalized_job_title=CompensationService.normalize_job_title(job_title),
            is_verified=True,
            is_flagged=False,
            created_at__gte=cutoff_date
        )

        if compensations.count() < 1:
            return Response(
                {
                    'message': 'Insufficient data for trend analysis',
                    'company_name': company.name,
                    'job_title': job_title
                },
                status=status.HTTP_403_FORBIDDEN
            )

        yearly_data = []
        current_year = datetime.now().year

        for year_offset in range(years):
            year = current_year - (years - 1 - year_offset)
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)

            year_avg = compensations.filter(
                created_at__gte=year_start,
                created_at__lte=year_end
            ).aggregate(avg=Avg('total_compensation'))['avg']

            yearly_data.append({
                'year': year,
                'average_salary': float(year_avg) if year_avg else None
            })

        first_valid = next((d['average_salary'] for d in yearly_data if d['average_salary']), None)
        last_valid = next((d['average_salary'] for d in reversed(yearly_data) if d['average_salary']), None)

        growth_percentage = 0.0
        trend_direction = 'stable'

        if first_valid and last_valid:
            growth_percentage = round(((last_valid - first_valid) / first_valid * 100), 2)
            if growth_percentage > 5:
                trend_direction = 'upward'
            elif growth_percentage < -5:
                trend_direction = 'downward'

        data = {
            'job_title': job_title,
            'company_name': company.name,
            'period': f'{years} years',
            'yearly_data': yearly_data,
            'growth_percentage': growth_percentage,
            'trend_direction': trend_direction
        }

        cache.set(cache_key, data, timeout=60 * 60 * 24)  # 24 hours
        return Response(data)


class LocationSalaryComparisonAPIView(APIView):
    """
    API view for salary comparison across locations.

    GET: Returns top 10 locations ranked by salary for a given job title and experience level.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 6 hours
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve salary data by location.

        Query Parameters:
            job_title: Job title (required)
            experience_level: Experience level - junior/mid/senior/lead (required)

        Returns:
            - Top 10 locations by average salary
            - Median salary for each location
            - Salary range (min/max)
            - Sample size

        Errors:
            - 400: Missing required parameters
        """
        job_title = request.GET.get('job_title')
        experience_level = request.GET.get('experience_level')

        if not job_title or not experience_level:
            return Response(
                {'error': 'job_title and experience_level parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'location_salary_{slugify(job_title)}_{experience_level}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        normalized_title = CompensationService.normalize_job_title(job_title)

        compensations = Compensation.objects.filter(
            normalized_job_title=normalized_title,
            experience_level=experience_level,
            is_verified=True,
            is_flagged=False
        ).values('location').annotate(
            avg_salary=Avg('total_compensation'),
            median_salary=Count('id'),
            min_salary=Min('total_compensation'),
            max_salary=Max('total_compensation'),
            count=Count('id')
        ).filter(count__gte=3).order_by('-avg_salary')[:10]

        results = []
        for comp in compensations:
            results.append({
                'location': comp['location'],
                'job_title': job_title,
                'experience_level': experience_level,
                'avg_salary': float(comp['avg_salary']) if comp['avg_salary'] else 0,
                'median_salary': float(comp['avg_salary']) if comp['avg_salary'] else 0,
                'salary_range': {
                    'min': float(comp['min_salary']) if comp['min_salary'] else 0,
                    'max': float(comp['max_salary']) if comp['max_salary'] else 0
                },
                'sample_size': comp['count']
            })

        cache.set(cache_key, results, timeout=60 * 60 * 6)  # 6 hours
        return Response(results)


class IndustrySalaryBenchmarkAPIView(ListAPIView):
    """
    API view for industry-wide salary benchmarks.

    GET: Returns aggregated salary data by industry with pagination.

    Permissions: AllowAny
    Pagination: StandardResultsSetPagination
    Throttling: AnalyticsThrottle
    Caching: 24 hours
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [AnalyticsThrottle]

    def get_queryset(self):
        """
        Retrieve industry benchmark data with aggregation.

        Query Parameters:
            industry: Industry type (required)
            experience_level: Experience level (optional)

        Returns:
            QuerySet of aggregated salary data
        """
        industry = self.request.GET.get('industry')
        experience_level = self.request.GET.get('experience_level')

        if not industry:
            return []

        cache_key = f'industry_benchmark_{industry}_{experience_level or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            self._cached_data = cached_data
            return cached_data

        companies = Company.objects.filter(industry=industry)

        compensations = Compensation.objects.filter(
            company__in=companies,
            is_verified=True,
            is_flagged=False
        )

        if experience_level:
            compensations = compensations.filter(
                experience_level=experience_level
            )

        grouped = compensations.values(
            'normalized_job_title',
            'experience_level'
        ).annotate(
            avg_salary=Avg('total_compensation'),
            median_salary=Count('id'),
            min_salary=Min('total_compensation'),
            max_salary=Max('total_compensation'),
            count=Count('id')
        ).filter(count__gte=5).order_by('-avg_salary')

        results = []
        for group in grouped:
            salaries = list(compensations.filter(
                normalized_job_title=group['normalized_job_title'],
                experience_level=group['experience_level']
            ).values_list('total_compensation', flat=True))

            if len(salaries) >= 5:
                salaries_sorted = sorted([float(s) for s in salaries])
                results.append({
                    'industry': industry,
                    'experience_level': group['experience_level'],
                    'job_title': group['normalized_job_title'],
                    'avg_salary': float(group['avg_salary']) if group['avg_salary'] else 0,
                    'median_salary': float(group['avg_salary']) if group['avg_salary'] else 0,
                    'p25': float(np.percentile(salaries_sorted, 25)),
                    'p75': float(np.percentile(salaries_sorted, 75)),
                    'sample_size': group['count']
                })

        cache.set(cache_key, results, timeout=60 * 60 * 24)  # 24 hours
        return results

    def get(self, request, *args, **kwargs):
        """
        Get industry salary benchmarks.

        Errors:
            - 400: Missing industry parameter
        """
        if not request.GET.get('industry'):
            return Response(
                {'error': 'industry parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset()
        if isinstance(queryset, list) and len(queryset) == 0:
            return Response(
                {'error': 'No data available for this industry'},
                status=status.HTTP_404_NOT_FOUND
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset)


class JobTitleAutocompleteAPIView(APIView):
    """
    API view for job title autocomplete suggestions.

    GET: Returns list of all normalized job titles matching query.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 24 hours
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    @method_decorator(cache_page(60 * 60 * 24))  # 24 hours
    def get(self, request):
        """
        Get autocomplete suggestions for job titles.

        Query Parameters:
            q: Search query (optional)
            limit: Maximum results to return (default: 20, max: 100)

        Returns:
            - List of matching normalized job titles
            - Count of records for each title
        """
        query = request.GET.get('q', '').lower().strip()
        limit = int(request.GET.get('limit', 20))

        if limit > 100:
            limit = 100

        if not query:
            job_titles = Compensation.objects.values('normalized_job_title').annotate(
                count=Count('id')
            ).order_by('-count')[:limit]
        else:
            job_titles = Compensation.objects.filter(
                normalized_job_title__icontains=query
            ).values('normalized_job_title').annotate(
                count=Count('id')
            ).order_by('-count')[:limit]

        results = [
            {
                'title': jt['normalized_job_title'],
                'count': jt['count']
            }
            for jt in job_titles
        ]

        return Response(results)


class PercentileDataAPIView(APIView):
    """
    API view for percentile salary breakdown.

    GET: Returns P10, P25, P50, P75, P90 with sample size.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 1 hour
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve percentile salary data.

        Query Parameters:
            job_title: Job title (required)
            company_id: Company identifier (optional)
            location: Location (optional)
            experience_level: Experience level (optional)

        Returns:
            - P10, P25, P50, P75, P90 percentiles
            - Sample size
            - Filtering criteria

        Errors:
            - 400: Missing job_title parameter
            - 403: Insufficient data for analysis
        """
        job_title = request.GET.get('job_title')
        company_id = request.GET.get('company_id')
        location = request.GET.get('location')
        experience_level = request.GET.get('experience_level')

        if not job_title:
            return Response(
                {'error': 'job_title parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'percentile_{slugify(job_title)}_{company_id or "all"}_{location or "all"}_{experience_level or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        normalized_title = CompensationService.normalize_job_title(job_title)

        queryset = Compensation.objects.filter(
            normalized_job_title=normalized_title,
            is_verified=True,
            is_flagged=False
        )

        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if location:
            queryset = queryset.filter(location=location)
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)

        if queryset.count() < 5:
            return Response(
                {
                    'message': 'Insufficient data available for percentile analysis',
                    'available_records': queryset.count()
                },
                status=status.HTTP_403_FORBIDDEN
            )

        salaries = sorted([
            float(s) for s in queryset.values_list('total_compensation', flat=True)
        ])

        data = {
            'job_title': job_title,
            'company': Company.objects.get(id=company_id).name if company_id else None,
            'location': location,
            'experience_level': experience_level,
            'p10': float(np.percentile(salaries, 10)),
            'p25': float(np.percentile(salaries, 25)),
            'p50': float(np.percentile(salaries, 50)),
            'p75': float(np.percentile(salaries, 75)),
            'p90': float(np.percentile(salaries, 90)),
            'sample_size': len(salaries)
        }

        cache.set(cache_key, data, timeout=60 * 60)  # 1 hour
        return Response(data)


class AnalyticsPlatformOverviewAPIView(APIView):
    """
    API view for platform-wide statistics overview.

    GET: Returns total reviews, companies, users, and recent activity.

    Permissions: AllowAny
    Throttling: AnalyticsThrottle
    Caching: 1 hour
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnalyticsThrottle]

    def get(self, request):
        """
        Retrieve platform statistics overview.

        No query parameters required.

        Returns:
            - Total reviews across platform
            - Total companies
            - Total compensation records
            - Verified companies count
            - Average company rating
            - Recent activity summary
        """
        cache_key = 'platform_overview'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        total_reviews = CompanyReview.objects.filter(
            is_verified=True,
            is_flagged=False
        ).count()

        total_companies = Company.objects.count()

        total_compensation = Compensation.objects.filter(
            is_verified=True,
            is_flagged=False
        ).count()

        verified_companies = Company.objects.filter(verified=True).count()

        avg_company_rating = CompanyReview.objects.filter(
            is_verified=True,
            is_flagged=False
        ).aggregate(avg=Avg('weighted_score'))['avg'] or 0

        recent_reviews = CompanyReview.objects.filter(
            is_verified=True,
            is_flagged=False
        ).select_related('company').order_by('-created_at')[:5]

        recent_activity = [
            {
                'type': 'review',
                'company': review.company.name,
                'rating': float(review.weighted_score),
                'timestamp': review.created_at.isoformat()
            }
            for review in recent_reviews
        ]

        data = {
            'total_reviews': total_reviews,
            'total_companies': total_companies,
            'total_compensation_records': total_compensation,
            'verified_companies': verified_companies,
            'average_company_rating': round(float(avg_company_rating), 2),
            'recent_activity': recent_activity
        }

        cache.set(cache_key, data, timeout=60 * 60)  # 1 hour
        return Response(data)


class CompanyRankingListAPIView(ListAPIView):
    """
    API view for ranked companies list.

    GET: Returns companies ranked by reputation and performance metrics.

    Permissions: AllowAny
    Pagination: StandardResultsSetPagination
    Throttling: AnalyticsThrottle
    Caching: 6 hours
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [AnalyticsThrottle]

    def get_queryset(self):
        """
        Retrieve companies ranked by combined metrics.

        Query Parameters:
            industry: Filter by industry (optional)
            limit: Maximum results (default: 20)

        Returns:
            Ranked list of companies
        """
        industry = self.request.GET.get('industry')
        limit = int(self.request.GET.get('limit', 20))

        queryset = Company.objects.filter(verified=True)

        if industry:
            queryset = queryset.filter(industry=industry)

        queryset = queryset.annotate(
            avg_salary=Avg('compensations__total_compensation')
        ).order_by('-reputation_index')[:limit]

        return queryset

    def get(self, request, *args, **kwargs):
        """Get ranked companies."""
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'error': 'No ranking data available'},
                status=status.HTTP_404_NOT_FOUND
            )

        results = []
        for rank, company in enumerate(queryset, 1):
            avg_salary = Compensation.objects.filter(
                company=company,
                is_verified=True,
                is_flagged=False
            ).aggregate(avg=Avg('total_compensation'))['avg'] or 0

            score = (company.reputation_index * 0.6 +
                    (company.review_count / 100) * 0.2 +
                    (float(avg_salary) / 100000) * 0.2)

            results.append({
                'rank': rank,
                'company_id': company.id,
                'company_name': company.name,
                'industry': company.industry,
                'reputation_index': company.reputation_index,
                'review_count': company.review_count,
                'avg_salary': float(avg_salary),
                'score': round(score, 3)
            })

        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(results)
