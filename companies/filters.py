import django_filters

from .models import Company


class CompanyFilter(django_filters.FilterSet):

    class Meta:

        model = Company

        fields = {
            "industry": ["exact"],
            "company_type": ["exact"],
            "verified": ["exact"],
            "manpower_size": ["exact"],
        }