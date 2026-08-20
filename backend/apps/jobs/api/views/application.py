from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.pagination import DefaultPagination
from apps.jobs.choices import ApplicationStatus
from apps.jobs.models import Application

from ..serializers import (
    ApplicationSerializer,
    ApplicationStatusHistorySerializer,
)
from .base import JobScopedViewSet


@extend_schema(tags=["Applications"])
class ApplicationViewSet(JobScopedViewSet):
    serializer_class = ApplicationSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Application.objects.filter(
            job=self.get_job(),
        ).select_related(
            "candidate",
            "candidate__city",
        )

        status_filter = self.request.query_params.get("status")
        candidate = self.request.query_params.get("candidate")
        search = self.request.query_params.get("search")

        if status_filter:
            queryset = queryset.filter(
                status__iexact=status_filter,
            )

        if candidate:
            queryset = queryset.filter(
                candidate_id=candidate,
            )

        if search:
            queryset = queryset.filter(
                Q(candidate__first_name__icontains=search)
                | Q(candidate__last_name__icontains=search)
                | Q(candidate__email__icontains=search)
            )

        ordering = self.request.query_params.get(
            "ordering",
            "-created_at",
        )

        allowed_ordering = {
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "status",
            "-status",
        }

        return queryset.order_by(
            ordering if ordering in allowed_ordering else "-created_at",
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = self.get_job()
        return context

    def perform_create(self, serializer):
        serializer.save(
            job=self.get_job(),
            created_by=self.request.user,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="status",
    )
    def update_status(self, request, *args, **kwargs):
        application = self.get_object()

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {
                    "status": [
                        "This field is required.",
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application.transition_to(
                new_status,
                changed_by=request.user,
            )
        except ValidationError as exc:
            return Response(
                exc.message_dict,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="history",
    )
    def history(self, request, *args, **kwargs):
        application = self.get_object()

        history = application.status_history.select_related(
            "changed_by",
        )

        serializer = ApplicationStatusHistorySerializer(
            history,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="notes",
    )
    def update_notes(self, request, *args, **kwargs):
        application = self.get_object()

        notes = request.data.get("notes")

        if notes is None:
            return Response(
                {
                    "notes": [
                        "This field is required.",
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.notes = notes
        application.save(
            update_fields=[
                "notes",
                "updated_at",
            ],
        )

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request, *args, **kwargs):
        summary = (
            Application.objects.filter(
                job=self.get_job(),
            )
            .values("status")
            .annotate(total=Count("id"))
        )

        pipeline = {status_value: 0 for status_value, _ in ApplicationStatus.choices}

        for item in summary:
            pipeline[item["status"]] = item["total"]

        return Response(
            {
                "total": sum(pipeline.values()),
                "pipeline": pipeline,
            },
            status=status.HTTP_200_OK,
        )
