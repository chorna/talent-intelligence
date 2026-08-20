from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from apps.jobs.models import (
    CandidateSubmission,
    ClientCandidateFeedback,
)

from ..serializers import ClientCandidateFeedbackSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Client Feedback"])
class FeedbackViewSet(JobScopedViewSet):
    serializer_class = ClientCandidateFeedbackSerializer

    def get_submission(self):
        return self.get_job_object_or_404(
            CandidateSubmission,
            id=self.kwargs["submission_id"],
        )

    def get_queryset(self):
        return (
            ClientCandidateFeedback.objects.filter(
                submission=self.get_submission(),
            )
            .select_related(
                "submission",
                "created_by",
            )
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = self.get_job()
        context["submission"] = self.get_submission()
        return context

    def perform_create(self, serializer):
        serializer.save(
            submission=self.get_submission(),
            created_by=self.request.user,
        )

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )
