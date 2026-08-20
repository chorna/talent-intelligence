from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet

from apps.candidates.models import CandidateImport
from apps.core.permissions import HasOrganization

from ..serializers.candidate_import import CandidateImportSerializer


@extend_schema(tags=["Candidate Imports"])
class CandidateImportViewSet(ModelViewSet):
    serializer_class = CandidateImportSerializer
    permission_classes = [HasOrganization]

    def get_queryset(self):
        return (
            CandidateImport.objects.filter(
                imported_by__organization_id=(self.request.user.organization_id),
            )
            .select_related(
                "candidate",
                "imported_by",
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        file = serializer.validated_data["file"]

        serializer.save(
            original_filename=file.name,
            imported_by=self.request.user,
        )
