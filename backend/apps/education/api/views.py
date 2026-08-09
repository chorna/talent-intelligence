from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.education.models import Education

from .serializers import EducationSerializer


class EducationViewSet(ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [AllowAny]
