from django.db.models import Q
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.models import Application, Job

from .serializers import (
    ApplicationSerializer,
    JobSerializer,
)


class JobViewSet(ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [HasOrganization]
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "title",
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Job.objects.filter(
            organization_id=self.request.user.organization_id,
        ).select_related(
            "organization",
            "created_by",
            "city",
        )

        status = self.request.query_params.get("status")
        work_mode = self.request.query_params.get("work_mode")
        employment_type = self.request.query_params.get(
            "employment_type",
        )
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")

        if status:
            queryset = queryset.filter(
                status__iexact=status,
            )

        if work_mode:
            queryset = queryset.filter(
                work_mode__iexact=work_mode,
            )

        if employment_type:
            queryset = queryset.filter(
                employment_type__iexact=employment_type,
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
                Q(title__icontains=search) | Q(description__icontains=search),
            )

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )


class ApplicationViewSet(ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Application.objects.select_related(
            "candidate",
            "job",
            "job__created_by",
        ).all()

        job = self.request.query_params.get("job")
        candidate = self.request.query_params.get("candidate")
        status = self.request.query_params.get("status")

        if job:
            queryset = queryset.filter(
                job_id=job,
            )

        if candidate:
            queryset = queryset.filter(
                candidate_id=candidate,
            )

        if status:
            queryset = queryset.filter(
                status__iexact=status,
            )

        return queryset
