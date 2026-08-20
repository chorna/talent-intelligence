from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.jobs.choices import InterviewStatus
from apps.jobs.models.interview import Interview

from ..serializers.interview import InterviewSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Interviews"])
class InterviewViewSet(JobScopedViewSet):
    serializer_class = InterviewSerializer

    def get_queryset(self):
        return (
            Interview.objects.filter(
                submission__job=self.get_job(),
            )
            .select_related(
                "submission",
                "submission__candidate",
            )
            .order_by("-scheduled_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = self.get_job()
        return context

    def perform_create(self, serializer):
        serializer.save()

    @action(
        detail=True,
        methods=["post"],
    )
    def complete(self, request, *args, **kwargs):
        interview = self.get_object()

        interview.status = InterviewStatus.COMPLETED
        interview.save(update_fields=["status", "updated_at"])

        return Response(
            self.get_serializer(interview).data,
            status=status.HTTP_200_OK,
        )
