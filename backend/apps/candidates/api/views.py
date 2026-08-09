from django.db.models import Q
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from apps.candidates.models import Candidate
from apps.core.pagination import DefaultPagination

from .serializers import CandidateSerializer


class CandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.select_related(
        "city",
        "city__country",
    ).prefetch_related(
        "skills",
        "experiences",
        "educations",
    )
    serializer_class = CandidateSerializer
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        skill = self.request.query_params.get("skill")
        skills = self.request.query_params.get("skills")
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")

        # Single skill:
        # ?skill=python
        if skill:
            queryset = queryset.filter(
                skills__slug__iexact=skill.strip(),
            )

        # Multiple skills (AND):
        # ?skills=python,django
        if skills:
            skill_slugs = [
                value.strip().lower() for value in skills.split(",") if value.strip()
            ]

            for skill_slug in skill_slugs:
                queryset = queryset.filter(
                    skills__slug__iexact=skill_slug,
                )

        if city:
            queryset = queryset.filter(
                city__name__iexact=city,
            )

        if country:
            queryset = queryset.filter(
                city__country__code__iexact=country,
            )

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(headline__icontains=search)
                | Q(summary__icontains=search)
            )

        return queryset.distinct()
