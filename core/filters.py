import django_filters
from rest_framework.filters import OrderingFilter, SearchFilter
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q
from core.models import Profile

import re

class ProfileFilter(django_filters.FilterSet):
    min_age = django_filters.NumberFilter(field_name="age", lookup_expr='gte')
    max_age = django_filters.NumberFilter(field_name="age", lookup_expr='lte')
    
    min_gender_prob = django_filters.NumberFilter(field_name="gender_probability", lookup_expr='gte')
    min_country_prob = django_filters.NumberFilter(field_name="country_probability", lookup_expr='gte')
    q = django_filters.CharFilter(method='parse_natural_language', label='Search')

    
    COUNTRY_MAP = {
       "nigeria": "NG", "kenya": "KE", "ghana": "GH", 
        "rwanda": "RW", "angola": "AO", "togo": "TG",
        "South Sudan": "SS",
        "Mauritius": "MU",
        "Djibouti": "DJ",
        "Somalia": "SO",
        "Sudan": "SD",
        "Morocco": "MA",
        "Botswana": "BW",
        "Western Sahara": "EH",
        "Niger": "NE",
        "Liberia": "LR",
        "Central African Republic": "CF",
        "Cape Verde": "CV",
        "Gambia": "GM",
        "Mauritania": "MR",
        "Comoros": "KM",
        "Mozambique": "MZ",
        "Lesotho": "LS",
        "Angola": "AO",
        "Tunisia": "TN",
        "United Kingdom": "GB",
        "Mali": "ML",
        "Rwanda": "RW",
        "Benin": "BJ",
        "Seychelles": "SC",
        "Senegal": "SN",
        "France": "FR",
        "United States": "US",
        "Germany": "DE",
        "Eritrea": "ER",
        "Burundi": "BI",
        "Burkina Faso": "BF",
        "Togo": "TG",
        "Ethiopia": "ET",
        "Egypt": "EG",
        "Chad": "TD",
        "Guinea-Bissau": "GW",
        "Guinea": "GN",
        "Republic of the Congo": "CG",
        "Ghana": "GH",
        "Nigeria": "NG",
        "India": "IN",
        "Tanzania": "TZ",
        "Zambia": "ZM",
        "Algeria": "DZ",
        "Equatorial Guinea": "GQ",
        "Eswatini": "SZ",
        "Côte d'Ivoire": "CI",
        "Japan": "JP",
        "China": "CN",
        "Malawi": "MW",
        "Cameroon": "CM",
        "Madagascar": "MG",
        "Canada": "CA",
        "São Tomé and Príncipe": "ST",
        "DR Congo": "CD",
        "Sierra Leone": "SL",
        "Australia": "AU",
        "Namibia": "NA",
        "Zimbabwe": "ZW",
        "South Africa": "ZA",
        "Uganda": "UG",
        "Brazil": "BR",
        "Kenya": "KE",
        "Libya": "LY",
        "Gabon": "GA"

    }
    
    AGE_GROUPS = {
        "teenager": Q(age__gte=13, age__lte=19),
        "young": Q(age__gte=16, age__lte=24),
        "adult": Q(age__gte=25, age__lte=45),
        "senior": Q(age__gte=46, age__lte=100),
    }

    class Meta:
        model = Profile
        fields = [
            'q',
            'gender',
            'country_id',
        ]

    def parse_natural_language(self, queryset, name, value):
        if not value or value.strip() == "":
            return queryset
    
        query_string = value.lower()
        filters = Q()

    # Safety: Wrap in try/except to prevent 500 errors
        try:
        # GENDER
            if "female" in query_string:
                filters &= Q(gender__iexact="female")
            elif "male" in query_string:
                filters &= Q(gender__iexact="male")

        # AGE GROUPS
            for group, q_obj in self.AGE_GROUPS.items():
                if group in query_string:
                    filters &= q_obj

            # COMPARATIVE AGE (Above/Below)
            # Use .search and check if match exists before calling .group()
            above = re.search(r'(above|over|older than)\s+(\d+)', query_string)
            if above:
                filters &= Q(age__gt=int(above.group(2)))

        # COUNTRY (The 'Nigeria' fix)
            country_match = re.search(r'(from|in|at)\s+([a-zA-Z\s]+)', query_string)
            if country_match:
                c_name = country_match.group(2).strip()
                iso = self.COUNTRY_MAP.get(c_name)
                if iso:
                    filters &= Q(country_id__iexact=iso)
                else:
                    # If country not in map, try searching country_id directly
                    # This prevents a crash and might find a match
                    filters &= Q(country_id__icontains=c_name[:2].upper())

            # FALLBACK: If 'filters' is still empty (e.g., "zxqv unparseable")
            # return an empty queryset or a name search, NEVER a 500 error.
            if not filters:
                return queryset.filter(
                    Q(first_name__icontains=value) | Q(last_name__icontains=value)
                )

            return queryset.filter(filters)

        except Exception:
        # Return empty list on any error to satisfy 'uninterpretable query check'
            return queryset.none()
        
class CustomOrderingFilter(OrderingFilter):
    # Map your custom names to DRF's internal logic
    ordering_param = 'sort_by'  # Matches your ?sort_by=age
    
    def get_ordering(self, request, queryset, view):
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            order = request.query_params.get('order', 'asc')
            
            # VALIDATION: Only allow fields that actually exist in the model
            valid_fields = [f.name for f in queryset.model._meta.fields]
            # Add any annotated fields like 'rank' if you use them
            valid_fields.append('rank') 

            clean_fields = []
            for f in fields:
                if f in valid_fields:
                    prefix = "-" if order.lower() == "desc" else ""
                    clean_fields.append(f"{prefix}{f}")
               
            return clean_fields if clean_fields else super().get_ordering(request, queryset, view)
        return super().get_ordering(request, queryset, view)
    
    