from drf_spectacular.utils import extend_schema

from apps.jobs.models import CandidateShortlist

from ..serializers.shorlist import CandidateShortlistSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Shortlist"])
class ShortlistViewSet(JobScopedViewSet):
    serializer_class = CandidateShortlistSerializer

    def get_queryset(self):
        return (
            CandidateShortlist.objects.filter(
                job=self.get_job(),
            )
            .select_related(
                "candidate",
                "created_by",
            )
            .order_by("-created_at")
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
