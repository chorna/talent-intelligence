from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.skills.models import Skill

from .serializers import SkillSerializer


class SkillViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
