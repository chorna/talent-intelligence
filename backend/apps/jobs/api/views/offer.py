from drf_spectacular.utils import extend_schema

from apps.jobs.models import CandidateSubmission, Offer

from ..serializers import OfferSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Offers"])
class OfferViewSet(JobScopedViewSet):
    serializer_class = OfferSerializer

    def get_submission(self):
        return self.get_job_object_or_404(
            CandidateSubmission,
            id=self.kwargs["submission_id"],
        )

    def get_queryset(self):
        return (
            Offer.objects.filter(
                submission=self.get_submission(),
            )
            .select_related(
                "submission",
                "submission__candidate",
                "submission__job",
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
        )
