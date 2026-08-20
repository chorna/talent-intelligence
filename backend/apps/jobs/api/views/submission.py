from drf_spectacular.utils import extend_schema

from apps.jobs.models import CandidateSubmission

from ..serializers import CandidateSubmissionSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Submissions"])
class SubmissionViewSet(JobScopedViewSet):
    serializer_class = CandidateSubmissionSerializer

    def get_queryset(self):
        return (
            CandidateSubmission.objects.filter(
                job=self.get_job(),
            )
            .select_related(
                "candidate",
                "client",
                "submitted_by",
            )
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = self.get_job()
        return context

    def perform_create(self, serializer):
        job = self.get_job()

        serializer.save(
            job=job,
            client=job.client,
            submitted_by=self.request.user,
        )
