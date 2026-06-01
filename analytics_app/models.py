from django.db import models
from companies.models import Company


class SalaryBenchmark(models.Model):
    """
    Pre-calculated salary benchmarks for performance optimization.
    Cached aggregations of compensation data.
    """
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="salary_benchmarks"
    )
    
    job_title = models.CharField(max_length=255)
    
    experience_level = models.CharField(
        max_length=50,
        choices=[
            ("junior", "Junior"),
            ("mid", "Mid Level"),
            ("senior", "Senior"),
            ("lead", "Lead"),
        ]
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    # Percentile data
    p25 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    p50 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    p75 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    average_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    median_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    data_points_count = models.PositiveIntegerField(
        default=0
    )
    
    last_updated = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        unique_together = [
            "company",
            "job_title",
            "experience_level",
            "location"
        ]
        indexes = [
            models.Index(fields=["job_title"]),
            models.Index(fields=["experience_level"]),
            models.Index(fields=["location"]),
            models.Index(fields=["last_updated"]),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.job_title} ({self.experience_level})"


class IndustrySalaryTrend(models.Model):
    """
    Industry-wide salary trends tracked over time.
    Used for trend analysis and market insights.
    """
    
    industry = models.CharField(max_length=255)
    
    year = models.IntegerField()
    
    month = models.IntegerField(
        null=True,
        blank=True
    )
    
    job_title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    average_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    
    median_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    
    total_entries = models.PositiveIntegerField()
    
    data_quality_score = models.FloatField(
        default=0.0,
        help_text="0-1 score indicating data reliability"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        unique_together = [
            "industry",
            "year",
            "month",
            "job_title"
        ]
        indexes = [
            models.Index(fields=["industry", "year"]),
            models.Index(fields=["job_title"]),
        ]
    
    def __str__(self):
        return f"{self.industry} - {self.year} - ${self.average_salary}"


class MarketInsight(models.Model):
    """
    Market-level insights and high-level statistics.
    Updated periodically from underlying data.
    """
    
    title = models.CharField(max_length=255)
    
    description = models.TextField()
    
    category = models.CharField(
        max_length=100,
        choices=[
            ("highest_paying_industry", "Highest Paying Industry"),
            ("fastest_growing_role", "Fastest Growing Role"),
            ("market_trend", "Market Trend"),
            ("skill_demand", "Skill Demand"),
            ("compensation_insight", "Compensation Insight"),
        ]
    )
    
    data = models.JSONField()
    
    confidence_score = models.FloatField(
        default=0.0,
        help_text="0-1 confidence in this insight"
    )
    
    source_data_count = models.PositiveIntegerField(
        help_text="Number of data points used"
    )
    
    valid_from = models.DateTimeField()
    
    valid_until = models.DateTimeField()
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        ordering = ["-confidence_score"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["valid_until"]),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.category})"
    
    def is_current(self):
        from django.utils import timezone
        now = timezone.now()
        return self.valid_from <= now <= self.valid_until


class CompanyRankingCache(models.Model):
    """
    Cached company rankings for performance.
    Regenerated periodically (e.g., daily).
    """
    
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="ranking_cache"
    )
    
    overall_rank = models.PositiveIntegerField()
    
    reputation_score = models.FloatField()
    
    review_count = models.PositiveIntegerField()
    
    avg_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    recommendation_percentage = models.FloatField()
    
    industry_rank = models.PositiveIntegerField()
    
    growth_trend = models.CharField(
        max_length=20,
        choices=[
            ("improving", "Improving"),
            ("stable", "Stable"),
            ("declining", "Declining"),
        ],
        default="stable"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ["overall_rank"]
        indexes = [
            models.Index(fields=["overall_rank"]),
            models.Index(fields=["industry_rank"]),
        ]
    
    def __str__(self):
        return f"{self.company.name} - Rank #{self.overall_rank}"
