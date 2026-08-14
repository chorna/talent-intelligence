from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.models import Application, Job

from .serializers import ApplicationSerializer, JobSerializer


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

        status_filter = self.request.query_params.get("status")
        work_mode = self.request.query_params.get("work_mode")
        employment_type = self.request.query_params.get(
            "employment_type",
        )
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")

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

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="applications",
    )
    def applications(self, request, pk=None):
        job = self.get_object()

        applications = Application.objects.filter(
            job=job,
        ).select_related(
            "candidate",
            "candidate__city",
        )

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @applications.mapping.post
    def create_application(self, request, pk=None):
        job = self.get_object()

        serializer = ApplicationSerializer(
            data=request.data,
            context={
                "request": request,
                "job": job,
            },
        )

        serializer.is_valid(raise_exception=True)

        application = serializer.save()

        return Response(
            ApplicationSerializer(
                application,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )
