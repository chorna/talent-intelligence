from rest_framework import serializers

from apps.candidates.models import Candidate
from apps.education.api.serializers import EducationSerializer
from apps.experiences.api.serializers import ExperienceSerializer
from apps.skills.api.serializers import SkillSerializer
from apps.skills.models import Skill


class CandidateSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(
        many=True,
        read_only=True,
    )

    skill_ids = serializers.PrimaryKeyRelatedField(
        source="skills",
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    experiences = ExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Candidate
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "headline",
            "summary",
            "linkedin_url",
            "github_url",
            "skills",
            "skill_ids",
            "experiences",
            "educations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "skills",
            "experiences",
            "educations",
            "created_at",
            "updated_at",
        ]

    def validate_email(self, value):
        return value.strip().lower()
