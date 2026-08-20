from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.api.serializers import JobSerializer
from apps.jobs.choices import ApplicationStatus, JobStatus
from apps.jobs.models import Application, Job


@extend_schema(tags=["Jobs"])
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
        queryset = (
            Job.objects.filter(
                organization_id=self.request.user.organization_id,
            )
            .select_related(
                "organization",
                "created_by",
                "city",
                "client",
            )
            .prefetch_related(
                "job_skills__skill",
            )
        )

        if self.action != "list":
            return queryset

        status_filter = self.request.query_params.get("status")
        work_mode = self.request.query_params.get("work_mode")
        employment_type = self.request.query_params.get(
            "employment_type",
        )
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")
        skill = self.request.query_params.get("skill")
        skills = self.request.query_params.get("skills")

        if status_filter:
            queryset = queryset.filter(
                status__iexact=status_filter,
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

        if skill:
            queryset = queryset.filter(
                job_skills__skill__slug__iexact=skill,
            )

        if skills:
            skill_slugs = [
                value.strip() for value in skills.split(",") if value.strip()
            ]

            for skill_slug in skill_slugs:
                queryset = queryset.filter(
                    job_skills__skill__slug__iexact=skill_slug,
                )

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["organization"] = self.request.user.organization

        return context

    @extend_schema(
        summary="Get organization dashboard",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="dashboard",
    )
    def dashboard(self, request):
        organization_id = request.user.organization_id

        jobs = Job.objects.filter(
            organization_id=organization_id,
        )

        applications = Application.objects.filter(
            job__organization_id=organization_id,
        )

        pipeline = {status_value: 0 for status_value in ApplicationStatus.values}

        pipeline_summary = applications.values("status").annotate(total=Count("id"))

        for item in pipeline_summary:
            pipeline[item["status"]] = item["total"]

        total_applications = applications.count()

        hired_rate = (
            round(
                pipeline[ApplicationStatus.HIRED] / total_applications * 100,
                2,
            )
            if total_applications
            else 0
        )

        rejected_rate = (
            round(
                pipeline[ApplicationStatus.REJECTED] / total_applications * 100,
                2,
            )
            if total_applications
            else 0
        )

        return Response(
            {
                "total_jobs": jobs.count(),
                "active_jobs": jobs.filter(
                    status=JobStatus.OPEN,
                ).count(),
                "total_applications": total_applications,
                "pipeline": pipeline,
                "metrics": {
                    "hired_rate": hired_rate,
                    "rejected_rate": rejected_rate,
                },
            },
            status=status.HTTP_200_OK,
        )
