from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from apps.jobs.models import JobSkill

from ..serializers.skill import JobSkillSerializer
from .base import JobScopedViewSet


@extend_schema(tags=["Job Skills"])
class JobSkillViewSet(JobScopedViewSet):
    serializer_class = JobSkillSerializer

    def get_queryset(self):
        return (
            JobSkill.objects.filter(
                job=self.get_job(),
            )
            .select_related(
                "skill",
            )
            .order_by("-created_at")
        )

    def get_object(self):
        return get_object_or_404(
            JobSkill,
            job=self.get_job(),
            skill_id=self.kwargs["pk"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = self.get_job()
        return context

    def perform_create(self, serializer):
        serializer.save(
            job=self.get_job(),
        )
