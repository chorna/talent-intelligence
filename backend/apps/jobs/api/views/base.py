from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import HasOrganization
from apps.jobs.models import Job


class JobScopedViewSet(ModelViewSet):
    permission_classes = [HasOrganization]

    def get_job(self):
        return get_object_or_404(
            Job,
            id=self.kwargs["job_id"],
            organization_id=self.request.user.organization_id,
        )

    def get_job_object_or_404(self, model, **filters):
        return get_object_or_404(
            model,
            job=self.get_job(),
            **filters,
        )
