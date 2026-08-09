from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.candidates.models import Candidate

from .serializers import CandidateSerializer


class CandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.prefetch_related(
        "skills",
        "experiences",
        "educations",
    )
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]
