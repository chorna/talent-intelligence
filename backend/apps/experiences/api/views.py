from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.experiences.models import Experience

from .serializers import ExperienceSerializer


@extend_schema(tags=["Experiences"])
class ExperienceViewSet(ModelViewSet):
    queryset = Experience.objects.select_related(
        "candidate",
    ).prefetch_related(
        "skills",
    )
    serializer_class = ExperienceSerializer
    permission_classes = [AllowAny]
