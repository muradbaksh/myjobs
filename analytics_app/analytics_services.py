"""
Comprehensive analytics services for the MYJOBS platform.

This module provides advanced analytics, fraud detection, benchmarking,
and ranking calculations for compensation, job markets, and company insights.
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import statistics

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from django.db.models import (
    Avg,
    Count,
    DecimalField,
    Q,
    QuerySet,
    Max,
    Min,
    Value,
)
from django.db.models.functions import Cast, ExtractYear
from django.utils import timezone
from django.core.exceptions import ValidationError

from compensation.models import Compensation
from companies.models import Company
from reviews.models import CompanyReview


class PercentileCalculator:
    """
    Calculates percentile distributions for compensation data.
    Uses numpy for efficiency if available, falls back to Django queries.
    """

    @staticmethod
    def calculate_percentiles(
        queryset: QuerySet,
        field: str = "total_compensation"
    ) -> Dict[str, Optional[Decimal]]:
        """
        Calculate percentiles (p10, p25, p50, p75, p90) for a given field.

        Args:
            queryset: Django QuerySet of Compensation objects
            field: Field name to calculate percentiles for

        Returns:
            Dictionary with keys: p10, p25, p50, p75, p90
            Returns None values if queryset is empty or has insufficient data.
        """
        # Filter to valid entries only
        valid_queryset = queryset.filter(
            is_verified=True,
            is_flagged=False
        )

        result = {
            "p10": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p90": None,
        }

        # Handle empty queryset
        if not valid_queryset.exists():
            return result

        # Extract values
        values = list(
            valid_queryset.values_list(field, flat=True).order_by(field)
        )

        if not values:
            return result

        # Use numpy if available for better performance
        if HAS_NUMPY:
            try:
                result["p10"] = Decimal(str(round(np.percentile(values, 10), 2)))
                result["p25"] = Decimal(str(round(np.percentile(values, 25), 2)))
                result["p50"] = Decimal(str(round(np.percentile(values, 50), 2)))
                result["p75"] = Decimal(str(round(np.percentile(values, 75), 2)))
                result["p90"] = Decimal(str(round(np.percentile(values, 90), 2)))
            except (TypeError, ValueError):
                # Fall back to Python if numpy fails
                result = PercentileCalculator._calculate_with_python(values)
        else:
            # Use Python's statistics module
            result = PercentileCalculator._calculate_with_python(values)

        return result

    @staticmethod
    def _calculate_with_python(values: List) -> Dict[str, Decimal]:
        """
        Calculate percentiles using Python's statistics module.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with percentile values
        """
        result = {
            "p10": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p90": None,
        }

        if not values:
            return result

        try:
            # Convert to float for calculations
            float_values = [float(v) for v in values]

            # Calculate percentiles manually
            sorted_values = sorted(float_values)
            n = len(sorted_values)

            def percentile(data, p):
                """Calculate percentile value."""
                k = (n - 1) * p / 100
                f = int(k)
                c = k - f

                if f + 1 < n:
                    return data[f] * (1 - c) + data[f + 1] * c
                return data[f]

            result["p10"] = Decimal(str(round(percentile(sorted_values, 10), 2)))
            result["p25"] = Decimal(str(round(percentile(sorted_values, 25), 2)))
            result["p50"] = Decimal(str(round(percentile(sorted_values, 50), 2)))
            result["p75"] = Decimal(str(round(percentile(sorted_values, 75), 2)))
            result["p90"] = Decimal(str(round(percentile(sorted_values, 90), 2)))
        except (ValueError, TypeError, IndexError):
            pass

        return result


class OutlierDetector:
    """
    Detects outliers in compensation data using the Interquartile Range (IQR) method.
    """

    @staticmethod
    def detect_outliers(
        queryset: QuerySet,
        field: str = "base_salary",
        iqr_multiplier: float = 1.5
    ) -> Tuple[int, Optional[Decimal], Optional[Decimal]]:
        """
        Detect outliers using IQR method.

        Args:
            queryset: Django QuerySet of Compensation objects
            field: Field to check for outliers
            iqr_multiplier: Multiplier for IQR (default 1.5 is standard)

        Returns:
            Tuple of (outlier_count, lower_bound, upper_bound)
        """
        # Filter to valid entries
        valid_queryset = queryset.filter(
            is_verified=True,
            is_flagged=False
        )

        if not valid_queryset.exists():
            return (0, None, None)

        # Get percentiles
        percentiles = PercentileCalculator.calculate_percentiles(
            queryset,
            field
        )

        q1 = percentiles.get("p25")
        q3 = percentiles.get("p75")

        if q1 is None or q3 is None:
            return (0, None, None)

        # Calculate IQR
        iqr = q3 - q1

        # Calculate bounds
        lower_bound = q1 - (iqr * Decimal(str(iqr_multiplier)))
        upper_bound = q3 + (iqr * Decimal(str(iqr_multiplier)))

        # Count outliers
        outlier_count = valid_queryset.filter(
            Q(**{f"{field}__lt": lower_bound}) |
            Q(**{f"{field}__gt": upper_bound})
        ).count()

        return (outlier_count, lower_bound, upper_bound)

    @staticmethod
    def flag_outliers_automatically(
        queryset: QuerySet,
        field: str = "base_salary",
        iqr_multiplier: float = 1.5,
        dry_run: bool = False
    ) -> int:
        """
        Automatically flag entries that are statistical outliers.

        Args:
            queryset: QuerySet to process
            field: Field to check
            iqr_multiplier: IQR multiplier
            dry_run: If True, only count without updating

        Returns:
            Number of entries flagged/to-be-flagged
        """
        outlier_count, lower_bound, upper_bound = OutlierDetector.detect_outliers(
            queryset,
            field,
            iqr_multiplier
        )

        if outlier_count == 0 or lower_bound is None or upper_bound is None:
            return 0

        # Find outlier entries
        outlier_entries = queryset.filter(
            Q(**{f"{field}__lt": lower_bound}) |
            Q(**{f"{field}__gt": upper_bound}),
            is_flagged=False
        )

        if not dry_run:
            for entry in outlier_entries:
                entry.is_flagged = True
                entry.moderation_note = (
                    f"Statistical outlier detected. {field}=${getattr(entry, field)} "
                    f"outside bounds [{lower_bound}, {upper_bound}]"
                )
                entry.save(update_fields=["is_flagged", "moderation_note"])

        return outlier_entries.count()


class JobTitleNormalizer:
    """
    Normalizes job titles to standard categories.
    Handles common variations and abbreviations.
    """

    MAPPING = {
        # Software Engineers
        "swe": "Software Engineer",
        "software engineer": "Software Engineer",
        "dev": "Software Engineer",
        "developer": "Software Engineer",
        "backend engineer": "Software Engineer",
        "backend developer": "Software Engineer",
        "frontend engineer": "Software Engineer",
        "frontend developer": "Software Engineer",
        "full stack engineer": "Software Engineer",
        "full stack developer": "Software Engineer",
        "fullstack engineer": "Software Engineer",
        "fullstack developer": "Software Engineer",
        "sr software engineer": "Software Engineer",
        "senior software engineer": "Software Engineer",
        "lead developer": "Software Engineer",
        "lead engineer": "Software Engineer",
        "staff engineer": "Software Engineer",
        "principal engineer": "Software Engineer",
        "platform engineer": "Software Engineer",
        "systems engineer": "Software Engineer",
        "application engineer": "Software Engineer",
        "application developer": "Software Engineer",
        "web developer": "Software Engineer",
        "web engineer": "Software Engineer",

        # Data Roles
        "data scientist": "Data Scientist",
        "data engineer": "Data Engineer",
        "machine learning engineer": "Data Scientist",
        "ml engineer": "Data Scientist",
        "data analyst": "Data Analyst",
        "analytics engineer": "Data Analyst",
        "bi engineer": "Data Analyst",
        "business intelligence": "Data Analyst",

        # Product & Design
        "product manager": "Product Manager",
        "pm": "Product Manager",
        "product owner": "Product Manager",
        "designer": "Designer",
        "ux designer": "Designer",
        "ui designer": "Designer",
        "product designer": "Designer",
        "ux/ui designer": "Designer",

        # DevOps & Infrastructure
        "devops engineer": "DevOps Engineer",
        "site reliability engineer": "DevOps Engineer",
        "sre": "DevOps Engineer",
        "infrastructure engineer": "DevOps Engineer",
        "cloud engineer": "DevOps Engineer",
        "aws engineer": "DevOps Engineer",

        # QA & Testing
        "qa engineer": "QA Engineer",
        "quality assurance": "QA Engineer",
        "test engineer": "QA Engineer",
        "automation engineer": "QA Engineer",
        "qa automation": "QA Engineer",

        # Management
        "manager": "Manager",
        "engineering manager": "Manager",
        "tech lead manager": "Manager",
        "director": "Director",
        "vp": "VP",
        "vice president": "VP",
        "cto": "CTO",
        "ceo": "CEO",

        # Business & Support
        "sales": "Sales",
        "sales engineer": "Sales",
        "business development": "Business Development",
        "account manager": "Account Manager",
        "customer success": "Customer Success",
        "support engineer": "Support Engineer",
        "technical support": "Support Engineer",

        # Other
        "consultant": "Consultant",
        "architect": "Architect",
        "security engineer": "Security Engineer",
        "cybersecurity": "Security Engineer",
    }

    @staticmethod
    def normalize(title: str) -> str:
        """
        Normalize a job title to a standard category.

        Args:
            title: Raw job title string

        Returns:
            Normalized job title
        """
        if not title:
            return "Unknown"

        # Convert to lowercase and strip whitespace
        normalized = title.lower().strip()

        # Check direct mapping
        if normalized in JobTitleNormalizer.MAPPING:
            return JobTitleNormalizer.MAPPING[normalized]

        # Check partial matches
        for key, value in JobTitleNormalizer.MAPPING.items():
            if key in normalized:
                return value

        # Return original if no match found
        return title.title()


class SalaryTrendAnalyzer:
    """
    Analyzes salary trends over time for companies and job titles.
    """

    @staticmethod
    def calculate_yoy_growth(
        company_id: Optional[int] = None,
        job_title: Optional[str] = None,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate year-over-year salary growth trends.

        Args:
            company_id: Optional company ID to filter by
            job_title: Optional job title to filter by
            years: Number of years to analyze (default 5)

        Returns:
            Dictionary with yearly data and overall growth percentage
        """
        result = {
            "yearly_data": [],
            "growth_percent": 0.0,
            "data_points": 0,
            "start_year": None,
            "end_year": None,
        }

        # Build base queryset
        queryset = Compensation.objects.filter(
            is_verified=True,
            is_flagged=False
        )

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        if job_title:
            queryset = queryset.filter(
                Q(job_title__icontains=job_title) |
                Q(normalized_job_title__icontains=job_title)
            )

        if not queryset.exists():
            return result

        # Calculate cutoff date
        now = timezone.now()
        cutoff_date = now - timedelta(days=365 * years)

        # Aggregate by year
        yearly_data = queryset.filter(
            created_at__gte=cutoff_date
        ).extra(
            select={"year": "YEAR(created_at)"}
        ).values("year").annotate(
            avg_salary=Avg("total_compensation"),
            count=Count("id")
        ).order_by("year")

        if not yearly_data:
            return result

        yearly_list = list(yearly_data)
        result["yearly_data"] = [
            {
                "year": item["year"],
                "average_salary": float(item["avg_salary"] or 0),
                "data_points": item["count"]
            }
            for item in yearly_list
        ]

        # Calculate growth
        if len(yearly_list) >= 2:
            first_year = yearly_list[0]
            last_year = yearly_list[-1]

            if first_year["avg_salary"] and last_year["avg_salary"]:
                growth = (
                    (float(last_year["avg_salary"]) - float(first_year["avg_salary"]))
                    / float(first_year["avg_salary"])
                ) * 100

                result["growth_percent"] = round(growth, 2)
                result["start_year"] = first_year["year"]
                result["end_year"] = last_year["year"]

        result["data_points"] = sum(item["count"] for item in yearly_list)

        return result


class CompanyRankingEngine:
    """
    Ranks companies based on multiple factors.
    Provides overall and industry-specific rankings.
    """

    @staticmethod
    def calculate_company_score(company: Company) -> float:
        """
        Calculate a comprehensive company score (0-100).

        Weights:
        - Reputation: 40% (weighted review score)
        - Review Count: 20% (normalized)
        - Recency: 15% (recent reviews weighted higher)
        - Salary Benchmark: 15% (compared to industry average)
        - Engagement: 10% (review/compensation activity ratio)

        Args:
            company: Company object to score

        Returns:
            Score between 0-100
        """
        score = 0.0

        # 1. Reputation Score (40%)
        reviews = CompanyReview.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        )

        if reviews.exists():
            reputation = float(reviews.aggregate(Avg("weighted_score"))["weighted_score__avg"] or 0)
            reputation_score = min(reputation, 100)
            score += reputation_score * 0.40
        else:
            score += 0  # No bonus if no reviews

        # 2. Review Count Score (20%)
        review_count = reviews.count()
        # Normalize: 50+ reviews = 100 points
        review_score = min((review_count / 50) * 100, 100)
        score += review_score * 0.20

        # 3. Recency Score (15%)
        recent_reviews = reviews.filter(
            created_at__gte=timezone.now() - timedelta(days=90)
        ).count()

        recency_score = min((recent_reviews / max(review_count, 1)) * 100, 100)
        score += recency_score * 0.15

        # 4. Salary Benchmark Score (15%)
        compensations = Compensation.objects.filter(
            company=company,
            is_verified=True,
            is_flagged=False
        )

        if compensations.exists():
            try:
                company_avg = float(
                    compensations.aggregate(Avg("total_compensation"))["total_compensation__avg"] or 0
                )

                # Compare to industry average
                industry_avg = float(
                    Compensation.objects.filter(
                        company__industry=company.industry,
                        is_verified=True,
                        is_flagged=False
                    ).aggregate(Avg("total_compensation"))["total_compensation__avg"] or 1
                )

                if industry_avg > 0:
                    salary_percentile = (company_avg / industry_avg) * 100
                    salary_score = min(salary_percentile, 100)
                    score += salary_score * 0.15
            except (TypeError, ValueError, ZeroDivisionError):
                pass

        # 5. Engagement Score (10%)
        comp_count = compensations.count()
        engagement_ratio = review_count / max(comp_count, 1)
        engagement_score = min(engagement_ratio * 50, 100)
        score += engagement_score * 0.10

        return round(score, 2)

    @staticmethod
    def top_companies(
        limit: int = 20,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top-ranked companies.

        Args:
            limit: Number of companies to return
            industry: Optional industry filter

        Returns:
            List of dictionaries with company info and scores
        """
        companies_qs = Company.objects.all()

        if industry:
            companies_qs = companies_qs.filter(industry=industry)

        companies_data = []

        for company in companies_qs[:limit * 2]:  # Get extra for sorting
            score = CompanyRankingEngine.calculate_company_score(company)
            companies_data.append({
                "company_id": company.id,
                "company_name": company.name,
                "industry": company.industry,
                "score": score,
                "review_count": company.review_count,
                "verified": company.verified,
            })

        # Sort by score descending
        companies_data.sort(key=lambda x: x["score"], reverse=True)

        return companies_data[:limit]


class FraudDetectionService:
    """
    Detects and flags suspicious or fraudulent entries.
    """

    @staticmethod
    def flag_suspicious_entries(
        deviation_threshold: float = 20.0,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Flag salary entries that deviate significantly from peer median.

        Args:
            deviation_threshold: Percentage deviation threshold (default 20%)
            dry_run: If True, only count without updating

        Returns:
            Dictionary with flagging statistics
        """
        result = {
            "total_checked": 0,
            "total_flagged": 0,
            "flagged_entries": [],
        }

        # Get all unverified compensations
        entries = Compensation.objects.filter(
            is_verified=True,
            is_flagged=False
        )

        result["total_checked"] = entries.count()

        for entry in entries:
            # Get peer median (same company, job title, experience level)
            peer_entries = Compensation.objects.filter(
                company=entry.company,
                normalized_job_title__iexact=entry.normalized_job_title,
                experience_level=entry.experience_level,
                is_verified=True,
                is_flagged=False
            ).exclude(id=entry.id)

            if not peer_entries.exists():
                continue

            # Calculate peer median
            median_salary = peer_entries.aggregate(Avg("total_compensation"))[
                "total_compensation__avg"
            ]

            if not median_salary:
                continue

            # Calculate deviation
            deviation_percent = abs(
                (float(entry.total_compensation) - float(median_salary)) / float(median_salary)
            ) * 100

            if deviation_percent > deviation_threshold:
                result["flagged_entries"].append({
                    "entry_id": entry.id,
                    "company": entry.company.name,
                    "salary": float(entry.total_compensation),
                    "peer_median": float(median_salary),
                    "deviation_percent": round(deviation_percent, 2),
                })

                if not dry_run:
                    entry.is_flagged = True
                    entry.moderation_note = (
                        f"Fraud detection: Salary deviates {round(deviation_percent, 2)}% "
                        f"from peer median of ${median_salary}"
                    )
                    entry.save(update_fields=["is_flagged", "moderation_note"])

                result["total_flagged"] += 1

        return result


class BenchmarkCalculator:
    """
    Calculates salary benchmarks for specific roles and companies.
    Includes K-anonymity checks for privacy.
    """

    MINIMUM_DATA_POINTS = 5  # K-anonymity minimum

    @staticmethod
    def calculate_benchmark(
        company_id: int,
        job_title: str,
        experience_level: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate salary benchmark for a specific role.

        Performs K-anonymity check (minimum 5 records) to ensure privacy.
        Only includes verified and non-flagged entries.

        Args:
            company_id: Company ID
            job_title: Job title to benchmark
            experience_level: Optional experience level filter
            location: Optional location filter

        Returns:
            Dictionary with benchmark data or None if insufficient data
        """
        # Build base queryset
        queryset = Compensation.objects.filter(
            company_id=company_id,
            is_verified=True,
            is_flagged=False
        )

        # Filter by job title (normalized or exact)
        queryset = queryset.filter(
            Q(normalized_job_title__iexact=job_title) |
            Q(job_title__icontains=job_title)
        )

        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)

        if location:
            queryset = queryset.filter(location__icontains=location)

        # K-anonymity check
        data_point_count = queryset.count()
        if data_point_count < BenchmarkCalculator.MINIMUM_DATA_POINTS:
            return None

        # Calculate benchmark metrics
        aggregates = queryset.aggregate(
            p10=Min("total_compensation"),  # Simplified p10
            p25=Min("total_compensation"),
            p50=Avg("total_compensation"),
            p75=Max("total_compensation"),
            p90=Max("total_compensation"),
            avg_salary=Avg("total_compensation"),
            median_salary=Avg("total_compensation"),
            min_salary=Min("total_compensation"),
            max_salary=Max("total_compensation"),
        )

        # Use PercentileCalculator for better percentiles
        percentiles = PercentileCalculator.calculate_percentiles(
            queryset,
            "total_compensation"
        )

        return {
            "company_id": company_id,
            "job_title": job_title,
            "experience_level": experience_level,
            "location": location,
            "data_points": data_point_count,
            "is_privacy_safe": data_point_count >= BenchmarkCalculator.MINIMUM_DATA_POINTS,
            "percentiles": {
                "p10": float(percentiles["p10"] or 0),
                "p25": float(percentiles["p25"] or 0),
                "p50": float(percentiles["p50"] or 0),
                "p75": float(percentiles["p75"] or 0),
                "p90": float(percentiles["p90"] or 0),
            },
            "average_salary": float(aggregates["avg_salary"] or 0),
            "median_salary": float(aggregates["median_salary"] or 0),
            "min_salary": float(aggregates["min_salary"] or 0),
            "max_salary": float(aggregates["max_salary"] or 0),
            "salary_range": {
                "min": float(aggregates["min_salary"] or 0),
                "max": float(aggregates["max_salary"] or 0),
            },
        }



# admin.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import CompanyReview
from companies.services import CompanyService

@receiver(post_save, sender=CompanyReview)
def update_company_reputation(sender, instance, **kwargs):
    if instance.is_verified and not instance.is_flagged:
        CompanyService.update_reputation_index(
            instance.company.id
        )